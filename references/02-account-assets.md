# 02 Account & Assets

All commands here require a valid API key. Run `cli.py check` first.

## Check (API key validation)

```bash
python3 scripts/cli.py check
```

Returns `{status, ...}` where status is `ok | no_token | invalid | no_balance | error`.
`invalid` means the server rejected the API key.

## Wallet

```bash
python3 scripts/cli.py wallet
```

`GET /finance/v1/wallet`. Fields: `recharge_balance` / `charge_balance_amount`,
`gift_balance_amount`, `total_balance_amount`.

## Whoami

```bash
python3 scripts/cli.py whoami
```

`GET /meta/v1/user/info` -> id, name, avatar, email, level, etc.

