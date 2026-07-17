# Data audit — request logs

- File: `data\raw\request_logs_raw.csv`
- Audit time UTC: `2026-07-17T14:28:00.584016+00:00`
- Shape: `5567` rows × `27` columns

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
id                         0
request_id                 0
timestamp                  0
user_id                   12
username                  12
is_authenticated           0
role                      12
session_id_hash           12
ip_address                 0
user_agent                 0
http_method                0
endpoint                   0
path                       0
action                     0
action_type                0
is_sensitive               0
resource_type           2794
resource_id             2794
owner_id                2820
permission              2782
ownership_result        2782
authorization_result       0
status_code                0
response_time_ms           0
file_size               3126
export_item_count       5567
export_total_size       5567
dtype: int64
```

## Distribution: `action_type`

```text
action_type
list           2758
view_detail    2296
create          242
edit            148
export           76
login            24
delete           23
Name: count, dtype: int64
```

## Distribution: `status_code`

```text
status_code
200    5275
302     230
404      62
Name: count, dtype: int64
```

## Distribution: `user_id`

```text
user_id
3.0       1174
6.0       1114
4.0       1106
2.0       1086
5.0       1075
<null>      12
Name: count, dtype: int64
```

## Distribution: `session_id_hash`

```text
session_id_hash
23b1773964a3b09ba16358e2f1613a844257b29604ce3a95682539f1918ed5a2    1088
6fdc642259692a6ac85ff2fb39ba9edc92454253b4983a9506995b08a7b11a3a    1087
10d60d4cad531b9bf6b97b0b2bb6301acca000ea9009fb17408ba2a36aebe1bf    1062
0ace177a47f5af4140dddaefae1fe38d8a25c178ae76fc06dad6be16ad614dee    1047
084f70f37d8c16e37747f4010586fd58f5945db9f8e5807b722899325515023d    1038
d30c87e33fa06078306a36a67bc5b2a9f4f7155491a42c8931e14fd79f634eb5      68
8ed8cae549bd386650bb8c580c33e49cb392c3e9535b87b6e71a0d3973f38ac2      53
751e61c47d18a2d009425ae2b30af18d6a0bde610a39dfb590c977dc74d8916c      33
99d9d3a6c56adfce630f153fa23d3fbc74c802e33a60ee083c585dae66a6bc2e      27
588cb50bba3d5260e257743d7962c1b414c92fbd26058b46a5afc5712a14aa78      23
f0d7a9c2cdc85d79a40935c4e649331777d7f7cd007889e1f05ec95746d9fd58      16
cf320a7cbdd08ab8d9a9e671bc4591cc7fd704e43d80ba0dc0bc8127361c2171      13
<null>                                                                12
Name: count, dtype: int64
```

## Distribution: `authorization_result`

```text
authorization_result
allowed    5505
denied       62
Name: count, dtype: int64
```

## Sensitive-data scan

- PASS: không thấy password/token/cookie/body nhạy cảm theo pattern cơ bản.
