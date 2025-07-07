# Movera
拉丁文 mover(移動) + era(時代)

> [!WARNING]  
> 請注意: 目前僅在 Synology NAS 上進行不完全測試，未在其他平台上進行充足的測試


使用 YAML 設定任務清單，並監控資料夾下的檔案，將符合條件的檔案重新命名與移動到指定資料夾

# 使用方法
有提供 [Docker image](https://hub.docker.com/r/thanatosdi/movera) 供快速啟動

`docker-compose.yaml`
```yaml
services:
  movera:
    image: thanatosdi/movera:latest
    container_name: movera
    environment:
      - MOVERA_CONFIG=/config/movera.yaml
    volumes:
      - ./config:/config
      - ./downloads:/watches/downloads
      - /Anime:/Anime
```
在 docker-compose.yaml 同層級目錄下建立 config 資料夾，在其中建立 movera.yaml 檔案

`movera.yaml`
```yaml
log:
  level: info
watches:
  - /watch/downloads
jobs:
  公爵千金的家庭教師:
    include: '公爵千金的家庭教師'
    move_to: '/Anime/公爵千金的家庭教師'
    src_filename_regex: '公爵千金的家庭教師 - (\d{2})(v2)? .+.mp4'
    dst_filename_regex: '公爵千金的家庭教師 - S01E\1 [1080P][WEB-DL][AAC AVC][CHT].mp4'
  膽大黨:
    include: 'Dan Da Dan'
    move_to: '/Anime/膽大黨/S02'
    src_filename_regex: '.+ Dan Da Dan \(2025\) \[(\d{2})\]\[AVC-8bit 1080p AAC\]\[CHT\].mp4'
    dst_filename_regex: '[Sakurato] Dan Da Dan (2025) [S02E\1][AVC-8bit 1080p AAC][CHT].mp4'
  example:
    include: 'example'
    move_to: '/Anime/example'
```

當有檔案放入到 `./downloads` 目錄下時會觸發 watchdog on_created 事件，會將檔案的絕對路徑放入 queue  
worker 會從 queue 取出檔案絕對路徑並進行處理

- 範例1: 
  ```
  檔案名稱為: 公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4
  符合 job => 公爵千金的家庭教師
  有設定 src_filename_regex 和 dst_filename_regex => 會執行重新命名
  檔案名稱格式符合 src_filename_regex 正規表示法取得 Group 1 => 01
  將檔案名稱重新命名為: 公爵千金的家庭教師 - S01E01 [1080P][WEB-DL][AAC AVC][CHT].mp4
  將檔案移動到 move_to 資料夾
  ```
- 範例2:
  ```
  檔案名稱為: [Sakurato] Dan Da Dan (2025) [13][AVC-8bit 1080p AAC][CHT].mp4
  符合 job => 膽大黨
  有設定 src_filename_regex 和 dst_filename_regex => 會執行重新命名
  檔案名稱格式符合 src_filename_regex 正規表示法取得 Group 1 => 13
  將檔案名稱重新命名為: [Sakurato] Dan Da Dan (2025) [S02E13][AVC-8bit 1080p AAC][CHT].mp4
  將檔案移動到 move_to 資料夾
  ```
- 範例3:
  ```
  檔案名稱為: example.mp4
  符合 job => example
  "沒有"設定 src_filename_regex 和 dst_filename_regex => 不會執行重新命名
  將檔案移動到 move_to 資料夾
  ```

# 設定檔說明

`movera.yaml` 的說明

- log:
  - level: log 的等級
- watches:
  - watch_path: 要監控的資料夾路徑
- jobs:
  - job_name:
    - include: 檔案名稱包含此字串
    - move_to: 要將檔案移動到的目的地資料夾
    - src_filename_regex: 檔案名稱格式符合的正規表示法
    - dst_filename_regex: 將檔案名稱重新命名的正規表示法



詳細正規表示法規則可以使用 [regex101.com](https://regex101.com/) 進行測試👍  
![image](https://github.com/user-attachments/assets/abc3b30d-a18e-4078-a530-7e621c4d3854)

dst_filename_regex 的重新命名規則使用可以使用 src_filename_regex 的 group，使用方式為直接在字串中使用 \1 \2 \3 來代表 group1 group2 group3
