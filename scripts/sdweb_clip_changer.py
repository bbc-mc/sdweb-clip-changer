# CLIP Changer
# bbc_mc

import torch
import ldm
import os

from modules import sd_models
from modules import paths, script_callbacks, shared
from modules import sd_hijack, sd_hijack_clip, sd_hijack_open_clip, sd_hijack_unet
from modules import call_queue
try:
    from modules import sd_hijack_xlmr, xlmr
except:
    print("  no module 'xlmr'. ignored")

DEBUG = False

def dprint(str, flg=False):
    if DEBUG or flg:
        print(str)

path_root = paths.script_path


def apply_clip(sd_model):
    dprint(f"DEBUG: shared.opts.enable_clipchanger: {shared.opts.enable_clipchanger}")

    if shared.opts.enable_clipchanger:

        _clip_text_model = shared.opts.clipchanger_target_clip_text_model
        _clip_tokenizer = shared.opts.clipchanger_target_clip_tokenizer

        from transformers import CLIPTextModel, CLIPTokenizer

        if _clip_text_model != "":
            try:
                sd_model.cond_stage_model.transformer = CLIPTextModel.from_pretrained(_clip_text_model).to(sd_model.cond_stage_model.transformer.device)
                sd_model.cond_stage_model.transformer.requires_grad_(False)
                print(f"  CLIPTextModel applied: {_clip_text_model}")
            except Exception as e:
                print(f"ERROR: loading CLIPTextModel [{_clip_text_model}]. skip")
                print(e)
        else:
            print(f"  CLIPTextModel not changed")

        if _clip_tokenizer != "":
            try:
                sd_model.cond_stage_model.tokenizer = CLIPTokenizer.from_pretrained(_clip_tokenizer)
                print(f"  CLIPTokenizer applied: {_clip_tokenizer}")
            except Exception as e:
                print(f"ERROR: loading CLIPTokenizer [{_clip_tokenizer}]. skip")
                print(e)
        else:
            print(f"  CLIPTokenizer not changed")

        if _clip_text_model != "" or _clip_tokenizer != "":
            sd_model.eval()
            shared.sd_model = sd_model

    return sd_model


def hijack_hijack(sd_model):
    if not shared.opts.enable_clipchanger:
        dprint( "  clip_change: not apply. Extension Disabled.")
        return

    flg_apply = False
    try:
        if type(sd_model.cond_stage_model) == xlmr.BertSeriesModelWithTransformation:
            dprint( "  clip_change: apply_clip. xlmr.BertSeriesModelWithTransformation")
            flg_apply = True
    except:
        print("  no module 'xlmr'. ignored")

    if type(sd_model.cond_stage_model) == ldm.modules.encoders.modules.FrozenCLIPEmbedder:
        dprint( "  clip_change: apply_clip. FrozenCLIPEmbedder")
        flg_apply = True
    elif type(sd_model.cond_stage_model) == sd_hijack_clip.FrozenCLIPEmbedderWithCustomWords:
        dprint( "  clip_change: apply_clip. FrozenCLIPEmbedderWithCustomWords")
        flg_apply = True

    if not flg_apply:
        dprint(f"  clip_change: not apply. type: {type(sd_model.cond_stage_model)}")
        return

    # at first, undo
    sd_hijack.model_hijack.undo_hijack(sd_model)

    # apply
    sd_model = apply_clip(sd_model)

    # apply lowvram/medvram if needed
    if shared.cmd_opts.lowvram or shared.cmd_opts.medvram:
        from modules import lowvram
        lowvram.setup_for_low_vram(sd_model, shared.cmd_opts.medvram)
        print(f"  VRAM-mode: {'LOWVRAM' if shared.cmd_opts.lowvram else 'MEDVRAM'}")
    else:
        sd_model.to(shared.device)
        print(f"  VRAM-mode: None")

    # re-do hijack
    sd_hijack.model_hijack.hijack(sd_model)


def on_ui_settings():

    # flg: Enable/Disable
    shared.opts.add_option("enable_clipchanger",
        shared.OptionInfo(False, "Enable CLIP Changer",
        section=("clip_changer", "CLIP Changer")))

    # txt: Clip encoder
    shared.opts.add_option("clipchanger_target_clip_text_model",
        shared.OptionInfo("", "Specify CLIPTextModel to use. [blank: use default]",
        section=("clip_changer", "CLIP Changer")))

    # txt: Clip encoder
    shared.opts.add_option("clipchanger_target_clip_tokenizer",
        shared.OptionInfo("", "Specify CLIPTokenizer to use. [blank: use default]",
        section=("clip_changer", "CLIP Changer")))


def on_model_loaded(sd_model):
    dprint(f"DEBUG: on_model_loaded:")
    try:
        shared.opts.enable_clipchanger
    except:
        dprint("DEBUG: on_model_loaded: shared not loaded. skip.")
        return

    hijack_hijack(sd_model)

def on_app_started(demo, app):

    list_must_be_before_them = ["lora_script.py"]

    callbacks_model_loaded = script_callbacks.callback_map.get("callbacks_model_loaded", None)

    if callbacks_model_loaded is None:
        return

    def find_script(name):
        for i, callback in enumerate(callbacks_model_loaded):
            callback:script_callbacks.ScriptCallback
            if os.path.basename(callback.script) == name:
                return i
        return None

    if len(callbacks_model_loaded) > 0:
        for index, callback in enumerate(callbacks_model_loaded):
            for file_before in list_must_be_before_them:
                callback:script_callbacks.ScriptCallback
                my_index = find_script("sdweb_clip_changer.py")
                if os.path.basename(callback.script) == file_before and my_index > index:
                    me = callbacks_model_loaded.pop(my_index)
                    callbacks_model_loaded.insert(index, me)
                    print(f"found {os.path.basename(callback.script)}. exchange my callback index {my_index} -> {index}")

    print("CLIP Changer.on_app_started done.")

#
script_callbacks.on_app_started(on_app_started)

#
script_callbacks.on_model_loaded(on_model_loaded)

#
script_callbacks.on_ui_settings(on_ui_settings)
