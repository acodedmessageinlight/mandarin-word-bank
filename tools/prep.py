FIX={'卡拉OK':'卡拉欧克','AA制':'诶诶制','我得参加':'我嘚参加','OK':'欧克'}
def prep(t):
    for k,v in FIX.items(): t=t.replace(k,v)
    return t.replace('…','，')
