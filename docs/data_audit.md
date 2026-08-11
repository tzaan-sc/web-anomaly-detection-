# Data audit — request logs

- File: `data\raw\request_logs_raw.csv`
- Audit time UTC: `2026-08-11T09:34:02.292236+00:00`
- Shape: `15628` rows × `27` columns

## Dtype

```text
id                        int64
request_id                  str
timestamp                   str
user_id                 float64
username                    str
is_authenticated          int64
role                        str
session_id_hash             str
ip_address                  str
user_agent                  str
http_method                 str
endpoint                    str
path                        str
action                      str
action_type                 str
is_sensitive              int64
resource_type               str
resource_id             float64
owner_id                float64
permission                  str
ownership_result            str
authorization_result        str
status_code               int64
response_time_ms        float64
file_size               float64
export_item_count       float64
export_total_size       float64
dtype: object
```

## Quality checks

- Duplicate request_id: `0`
- Timestamp parse errors: `0`
- response_time_ms numeric errors: `0`
- `is_authenticated` values: `['0', '1']`
- `is_sensitive` values: `['0', '1']`

## Null counts

```text
id                          0
request_id                  0
timestamp                   0
user_id                    49
username                   49
is_authenticated            0
role                       49
session_id_hash            52
ip_address                  0
user_agent                  0
http_method                 0
endpoint                    0
path                        0
action                      0
action_type                 0
is_sensitive                0
resource_type            7949
resource_id              7949
owner_id                 8027
permission               7767
ownership_result         7767
authorization_result        0
status_code                 0
response_time_ms            0
file_size                8899
export_item_count       15628
export_total_size       15628
dtype: int64
```

## Distribution: `action_type`

```text
action_type
list           7723
view_detail    6352
create          654
edit            388
export          225
login            85
admin            69
delete           67
other            65
Name: count, dtype: int64
```

## Distribution: `status_code`

```text
status_code
200    14739
302      641
404       96
403       92
304       60
Name: count, dtype: int64
```

## Distribution: `user_id`

```text
user_id
3.0       3310
6.0       3137
4.0       3104
5.0       2982
2.0       2913
1.0        133
<null>      49
Name: count, dtype: int64
```

## Distribution: `session_id_hash`

```text
session_id_hash
72634081a9945a46da1e2849594d3ec4b5ed79fb1d6b2eabb38752031ac52c0c    2194
718af66ee1399327895f1baf208bbaabf04b87a72a13231795f71dc13a16f1a2    2166
ee38e16729272e933822f44f52f731c40ce8839288b6d825ba34f5e2dd9c25f4    2097
0102d50e807764919b20c62c7fbda02c35b1f656845d3873c83ab02500f2eb8d    2091
c3936029d5d99f541ffd7497741f1b2a797c496310fa645b04d93eace22b2cfe    2072
e9a6374a11465016cd0853ed44aa48b3fe8cf65ca551b3e754cd687f7abb8b16     449
d55cd57f369148116a8f6b89f33efe66d4a8bce2e7d2d0a237ba96ce1e64b032     441
a8a9bccc1c9ad95ecfac4cfda8a91ab60c2ee95389ee61dc358e5d3b00934af7     429
681bca8d80aba5792e2bebd5816a2381bc847e8b1ab4b9be0814a55d8f064ec4     429
ba75dcb731e9bd24397937d35fdba71b9a91de73034befbfe76f13a3dacd42bc     423
1c18ad178387b25d93917d293525d15da1dd3cc7a17d70bb9bb981310ec02c55     423
17fdcf617626fef75015a23a2c654b94b93c5e66961e1a0615c64cdee94b29f2     417
338aa7412e93a8f60ddd4e742957770ea104a1911875233650b07f56bf83066a     417
a6ea3cddd94198372caf0a6125464cd7965154ea2ab522949af44b09f8b68fa7     411
94ecbdb484cf62265f52faea01ff0801e21cae653cbcaebef9578de0e3a4cec8     286
675b9cf518cf133b0effd337e59fb351cb32b31b8b9c71348d3942095a88b972      72
bb544f60127abacd013d0bc2b781acfb83d51696b96faa38353b52b675b41fdf      68
58fb378eebd9c25a3d77419d686e57bfb9a75b405957eefe67c47eb01b365fe0      68
eecb2a7f21cd3d7f1d83288614cd8cba4e50d4fcacd8db82a32b90d2808c60bb      68
6ee3a82a1a1f293e97cf9dc999bb8fee8679707cecac50c3025041c5219c0fd8      53
541c4f80227f0876b3c4cf5b5978a531db703439fcc289b1489b5f7198830407      53
ce72213edeae80ae0faf3d29da14501cf2a3f95c295f697d6b1be2dcba2e7938      53
<null>                                                                52
5156868d99542344dc7be015a6fdc62db8a2ab446856211e99376199bcc398e2      33
97d4fd914c706c970800978b5159f84cc0cd14dc2d8f82ba116d95b331d489d9      33
c9d759d98eecc9fe12be01ca1fe01f59568a8bfef8482a2f45d96e43114d81d2      33
f9680eea217c5cedfca879317c8deb9a58f5ad19d694d8d34ad50b68488a06ee      27
1e7c0b9b50c77375c46079584bc3f85ee85e9852404b1fb4836f176f9f2dedaf      27
3241d2b7ade74875f06eef9cdfb8628d615697bdf49265de53ae5e781cd3cf2a      27
216614a2887cb5b5176eafe126c61a6781cd05d27b7eab49782f2bb1067c3480      26
Name: count, dtype: int64
```

## Distribution: `authorization_result`

```text
authorization_result
allowed    15440
denied       188
Name: count, dtype: int64
```

## Sensitive-data scan

- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.
