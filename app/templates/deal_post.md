# {{ deal.title }}

[![{{ deal.title }}]({{ deal.image_url }})]({{ deal.url }})

| Details | |
| - | - |
| &#127991; **Coupon Code** | {{ deal.coupon_code if deal.coupon_code else '&#10060;' }} |
| &#127758; **Country** | {% if deal.global %}multiple ([check details]({{ deal.url }})){% else %}![{{ deal.country_code }}](https://steemitimages.com/22x22/https://github.com/hjnilsson/country-flags/raw/master/png100px/{{ deal.country_code }}.png){% endif %} |
| &#128198; **Starts** | {{ deal.date_start|datetimeformat }} |
| &#128198; **Ends** | {{ deal.date_end|datetimeformat }} |
| &#128176; **Freebie?** | {{ '&#128077;' if deal.freebie else '&#10060;' }} |
| &#128279; **Deal Link** | [{{ deal.title | truncate(40, True) }}]({{ deal.url }}) |

## Description

{{ deal.description }}

---
### Find more deals or earn Steem for posting deals on [BlockDeals](https://blockdeals.org) today!
[![](https://blockdeals.org/assets/images/blockdeals_logo.png)](https://blockdeals.org)
