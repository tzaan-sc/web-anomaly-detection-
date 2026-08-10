# Data audit — request logs

- File: `data\raw\request_logs_raw.csv`
- Audit time UTC: `2026-08-10T06:52:18.306062+00:00`
- Shape: `21401` rows × `27` columns

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
user_id                  5152
username                 5152
is_authenticated            0
role                     5152
session_id_hash          5152
ip_address                  0
user_agent                  0
http_method                 0
endpoint                    0
path                        0
action                      0
action_type                 0
is_sensitive                0
resource_type           12310
resource_id             12310
owner_id                13378
permission               8015
ownership_result         8015
authorization_result        0
status_code                 0
response_time_ms            0
file_size               14350
export_item_count       21401
export_total_size       21401
dtype: int64
```

## Distribution: `action_type`

```text
action_type
list           9705
view_detail    7467
login          2561
create          824
edit            454
export          160
other            93
admin            92
delete           45
Name: count, dtype: int64
```

## Distribution: `status_code`

```text
status_code
200    18001
302     3246
304       91
404       32
403       31
Name: count, dtype: int64
```

## Distribution: `user_id`

```text
user_id
<null>    5152
3.0       3396
6.0       3267
4.0       3188
5.0       3176
2.0       3037
1.0        185
Name: count, dtype: int64
```

## Distribution: `session_id_hash`

```text
session_id_hash
<null>                                                              5152
592f63953ceae157e91381d222098e5739bc2240a67cc1c5726f54041e820f74    3310
c9879ba495eb7d18d9e24141ab18587c74fe78c41fa41acb86fcbbc28cc1e216    3240
d5765b05e07b810fe64ff5c47a4071f74186305c9ebcb9686f80ce25d9335efe    3163
54591b2e6fa9b327247f9c4d4f459dc20303046959ae22cb61140168620597b3    3120
509d59c0344fa41cba89cf2ec1f84f916ad6821eaf0f58d0d67fefa8936a5c6a    2998
3e2fcb86522105613111ab82e5c35242de4cbb818c39572f85efece739900119     185
fce27a85fce604f864ec347354f6da3b9ad2cf579f571b6241a19ae5f60954cc      68
7e6ef1b9196c8965fb158ca836a53ea77db59c5f3c2a4c9c43467f11e2176b99      53
23097eb7495dd07fddfda3157c7ef470d0e02badb7c81a31fd15ec021e2bcf21      33
28161fc8b9b93b2135f5ca095a72c157cf52f14d2deb87bd6cf90175c88bddab      27
b741825fcae24f139a6bd7a99e0ac2a61157db44e936c6a7796a998e7ae5acd6      23
bb441055f51ef734aa1dccdb8dd6ccc4bd8779acb592324d3907b22198f90f7e      16
10142d277b8b2e91df8a0d5a8c974ffbcf5ad995b2c4d1601f73d53dd2847485      13
Name: count, dtype: int64
```

## Distribution: `authorization_result`

```text
authorization_result
allowed    21338
denied        63
Name: count, dtype: int64
```

## Sensitive-data scan

- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.
