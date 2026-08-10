# Data audit — request logs

- File: `data\raw\request_logs_raw.csv`
- Audit time UTC: `2026-08-10T07:56:07.753645+00:00`
- Shape: `52700` rows × `27` columns

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
resource_type           32776
resource_id             32776
owner_id                32802
permission              32724
ownership_result        32724
authorization_result        0
status_code                 0
response_time_ms            0
file_size               36014
export_item_count       52700
export_total_size       52700
dtype: int64
```

## Distribution: `action_type`

```text
action_type
list           33229
view_detail    15784
create          2324
edit             848
export           371
delete            80
login             24
admin             20
other             20
Name: count, dtype: int64
```

## Distribution: `status_code`

```text
status_code
200    50939
302     1678
404       32
403       31
304       20
Name: count, dtype: int64
```

## Distribution: `user_id`

```text
user_id
3.0       10692
6.0       10614
2.0       10479
4.0       10457
5.0       10406
1.0          40
<null>       12
Name: count, dtype: int64
```

## Distribution: `session_id_hash`

```text
session_id_hash
ab8d22d11121d30478ce7bd5ee207f20a119aff94b9991260bef1c63350c2f41    10606
2777c0e01221da77efe2ab46587be497c0f79df63f48bf1384da81582b41af79    10587
5678d99b79dc68c3418421e564a75da82261b33753399fa7caab303c23e8ac43    10440
fda49cfe378e258b96a7050aa68618a3042a72416e168eb30c06ddbf4eecb68a    10393
a3dd711c421737b6a117c3216633d25ceb616f573b67c08a2b542db7b130cc15    10389
fb887f4c0a707ede1a27e44c463ddc44c1aef4ece3b191692e0cc59b0aa01b18       68
8bdf952a7d30910d910f2acd868258ac04276fe41d8e555aa7681e1e5fb44495       53
3e2fcb86522105613111ab82e5c35242de4cbb818c39572f85efece739900119       40
a1c3d9823bb1618af382992bfa0fc9af1f4c9e7900ff5e3048b4c694c7954f4b       33
49f40f9e8505bc5bfb46f2731cd08719b044aa6728b460648f11578912e09544       27
fffd28fb5b64b47a9a8ef44fc925ef1557b3b2c667eb661f0bc110ed7117a858       23
c6f9c69d54f188695114a041bf3c49ca4abdb50a83479a831dc0e679fe4cfb33       16
9e4483951e8425c738d14198bedcb2f096cbe4ac02790317325440b8eb966d8e       13
<null>                                                                 12
Name: count, dtype: int64
```

## Distribution: `authorization_result`

```text
authorization_result
allowed    52637
denied        63
Name: count, dtype: int64
```

## Sensitive-data scan

- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.
