# CLIP changer

![](misc/clipchange_00.png)

[English README](README.md)

- [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) 用の Extension です
- CLIP エンコーダを他のものに差し替える機能と、設定画面を提供します

## 更新情報

- 2023/06/06: オプションで lowvram/midvram を選択した場合の処理を追加
  
   - lowvram/midvram を選択した場合に clip changer 適用後にモデルが cpu と gpu に分かれて配置されてしまう問題に対応



## インストール方法

- `Extensions` タブを開く
- `Install from URL` にこのレポジトリの URL を入力
- `Install` を実行

## 使い方 / How to use

- "設定" タブを開く
- 設定欄に、使用する CLIP を選択する

## 注意事項

モデルがロードされた時に、オンメモリで保持されているモデルデータの CLIP を差し替えます。そのため、

- 設定変更しても、モデルをロードするまでは適用されません

- 設定を OFF にしても、モデルをロードし直すまで適用されたままです

モデルマージ時には、どの CLIP がロードされているか、注意してください

## 設定項目について

![](misc/clipchange_00.png)

| In "Setting" tab              |                      |
| ----------------------------- | -------------------- |
| Enable CLIP Changer           | この Extension を有効にします |
| Specify CLIPTextModel to use. | 使用する CLIP を指定してください。 |
| Specify CLIPTokenizer to use. | 使用する CLIP を指定してください。 |

CLIPTextModel, CLIPTokenizer は diffusers ライブラリを使用するため、対応しているものを使用ください

```python
from transformers import CLIPTextModel, CLIPTokenizer
```

## 設定サンプル

- 以下のデータで、動作テストを行いました
  
   - `openai/clip-vit-large-patch14`
   - `openai/clip-vit-large-patch14-336`

- 設定画面例

![](misc/clipchange_01.png)

## Special Thanks

- [「[WebUI] Stable DiffusionベースモデルのCLIPの重みを良いやつに変更する」](https://zenn.dev/discus0434/articles/7ada798c5cc87d)
