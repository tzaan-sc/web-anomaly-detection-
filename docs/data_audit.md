# Data audit — request logs

- File: `data\raw\request_logs_raw.csv`
- Audit time UTC: `2026-08-12T05:52:58.414568+00:00`
- Shape: `10875` rows × `27` columns

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
resource_type            5515
resource_id              5515
owner_id                 5541
permission               5493
ownership_result         5493
authorization_result        0
status_code                 0
response_time_ms            0
file_size                6174
export_item_count       10875
export_total_size       10875
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
admin             5
other             5
Name: count, dtype: int64
```

## Distribution: `status_code`

```text
status_code
200    10386
302      421
404       32
403       31
304        5
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
1.0         10
Name: count, dtype: int64
```

## Distribution: `session_id_hash`

```text
session_id_hash
ea237752f73623591adc1111f6d71b8412fba4c49fadf45201a95ea6fec53e95    2194
b478ac99dd0ce00200d46f877a548aeb082634ac1fde71d074629386713108a4    2166
22658b822da6f21ec09fd1ad6b5d75261f4531a860caa308f270460116b0eba2    2097
29d88ae6a299305f8047c62b16bd2011036839d5b04eca30b87aa0e58f9e8813    2091
9b2e94d44d1ef8520af2d3e8fe05a1e9191da31c96716f08b60e18a5f9b23c51    2072
919f0dfa4b897ce1b6197e65137397942d602aa65a0092bb1e6b2283a0cfef84      68
160885efd5b9405dd7fcca21cc122712198c072979a65a4dd845e1a0e52b91b2      53
d6e82b13644b4b16a58619d636ad44cb7eae21269e5bc7f770558ff25ea0f5a6      33
37821511d5ccaa4062b6d1e011702d6f1fb2d3e244aabcdf2ec033476da88c88      27
83308f7d4e8abc141be6f169eade95592880093fca42fa6084cc95f4463106ff      23
fe6081df967830c19a8cf3ac0073aab5d3870e568aa0d8fad3e964f1f41a5c5f      16
b1a3367d04a80dbcdd8813068aefc18d909dd7ecae6efd64d518fe7cfc951892      13
<null>                                                                12
50aad02d8baf4da68ec29e8f1f10278198bbc5d968d13ced75986679b339a490      10
Name: count, dtype: int64
```

## Distribution: `authorization_result`

```text
authorization_result
allowed    10812
denied        63
Name: count, dtype: int64
```

## Sensitive-data scan

- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.
