# Data audit — request logs

- File: `data\raw\request_logs_raw.csv`
- Audit time UTC: `2026-08-10T08:50:11.997191+00:00`
- Shape: `10867` rows × `27` columns

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
user_id                    12
username                   12
is_authenticated            0
role                       12
session_id_hash            12
ip_address                  0
user_agent                  0
http_method                 0
endpoint                    0
path                        0
action                      0
action_type                 0
is_sensitive                0
resource_type            5507
resource_id              5507
owner_id                 5533
permission               5493
ownership_result         5493
authorization_result        0
status_code                 0
response_time_ms            0
file_size                6166
export_item_count       10867
export_total_size       10867
dtype: int64
```

## Distribution: `action_type`

```text
action_type
list           5534
view_detail    4408
create          466
edit            286
export          114
delete           33
login            24
admin             1
other             1
Name: count, dtype: int64
```

## Distribution: `status_code`

```text
status_code
200    10382
302      421
404       32
403       31
304        1
Name: count, dtype: int64
```

## Distribution: `user_id`

```text
user_id
3.0       2280
6.0       2193
4.0       2140
2.0       2130
5.0       2110
<null>      12
1.0          2
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
bb544f60127abacd013d0bc2b781acfb83d51696b96faa38353b52b675b41fdf      68
6ee3a82a1a1f293e97cf9dc999bb8fee8679707cecac50c3025041c5219c0fd8      53
5156868d99542344dc7be015a6fdc62db8a2ab446856211e99376199bcc398e2      33
f9680eea217c5cedfca879317c8deb9a58f5ad19d694d8d34ad50b68488a06ee      27
dd3dd52cde4e213ebf7fb8fdbc9556085edf3cf54b028c27f4a28fa23174f9db      23
559a1c61c7e01750dc28366b1247cfbd2eebe9b5256da6833010cafbe8385f29      16
5049dbac75d53f8e64099746d3fdfd8cfe8f43207398f4596b6ba85527709f5e      13
<null>                                                                12
3e2fcb86522105613111ab82e5c35242de4cbb818c39572f85efece739900119       2
Name: count, dtype: int64
```

## Distribution: `authorization_result`

```text
authorization_result
allowed    10804
denied        63
Name: count, dtype: int64
```

## Sensitive-data scan

- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.
