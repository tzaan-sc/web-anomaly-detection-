# Data audit — request logs

- File: `data\raw\request_logs_raw.csv`
- Audit time UTC: `2026-08-11T01:17:28.277380+00:00`
- Shape: `13125` rows × `27` columns

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
user_id                    25
username                   25
is_authenticated            0
role                       25
session_id_hash            25
ip_address                  0
user_agent                  0
http_method                 0
endpoint                    0
path                        0
action                      0
action_type                 0
is_sensitive                0
resource_type            6637
resource_id              6637
owner_id                 6689
permission               6602
ownership_result         6602
authorization_result        0
status_code                 0
response_time_ms            0
file_size                7437
export_item_count       13125
export_total_size       13125
dtype: int64
```

## Distribution: `action_type`

```text
action_type
list           6589
view_detail    5354
create          566
edit            336
export          171
delete           50
login            48
other             6
admin             5
Name: count, dtype: int64
```

## Distribution: `status_code`

```text
status_code
200    12469
302      525
404       64
403       62
304        5
Name: count, dtype: int64
```

## Distribution: `user_id`

```text
user_id
3.0       2795
6.0       2669
4.0       2625
5.0       2546
2.0       2455
<null>      25
1.0         10
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
a8a9bccc1c9ad95ecfac4cfda8a91ab60c2ee95389ee61dc358e5d3b00934af7     429
ba75dcb731e9bd24397937d35fdba71b9a91de73034befbfe76f13a3dacd42bc     423
17fdcf617626fef75015a23a2c654b94b93c5e66961e1a0615c64cdee94b29f2     417
94ecbdb484cf62265f52faea01ff0801e21cae653cbcaebef9578de0e3a4cec8     286
bb544f60127abacd013d0bc2b781acfb83d51696b96faa38353b52b675b41fdf      68
58fb378eebd9c25a3d77419d686e57bfb9a75b405957eefe67c47eb01b365fe0      68
6ee3a82a1a1f293e97cf9dc999bb8fee8679707cecac50c3025041c5219c0fd8      53
541c4f80227f0876b3c4cf5b5978a531db703439fcc289b1489b5f7198830407      53
5156868d99542344dc7be015a6fdc62db8a2ab446856211e99376199bcc398e2      33
97d4fd914c706c970800978b5159f84cc0cd14dc2d8f82ba116d95b331d489d9      33
f9680eea217c5cedfca879317c8deb9a58f5ad19d694d8d34ad50b68488a06ee      27
1e7c0b9b50c77375c46079584bc3f85ee85e9852404b1fb4836f176f9f2dedaf      27
<null>                                                                25
dd3dd52cde4e213ebf7fb8fdbc9556085edf3cf54b028c27f4a28fa23174f9db      23
ee5c17f541e6735096e1253b79bfa643965bd6210d38cabfadcbf5c2a9f41248      23
559a1c61c7e01750dc28366b1247cfbd2eebe9b5256da6833010cafbe8385f29      16
31bb6af6e5094369c6e361f7aa4db1526137d8ecf5883ea4c8400fc02c12cbd5      16
5049dbac75d53f8e64099746d3fdfd8cfe8f43207398f4596b6ba85527709f5e      13
5a7be607018bcbbe8293e7c2dc53a6ae570f2c595909a210d905d9be8292354f      13
3e2fcb86522105613111ab82e5c35242de4cbb818c39572f85efece739900119      10
Name: count, dtype: int64
```

## Distribution: `authorization_result`

```text
authorization_result
allowed    12999
denied       126
Name: count, dtype: int64
```

## Sensitive-data scan

- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.
