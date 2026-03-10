"""
财务记账模块
"""
from datetime import date
import storage


CATEGORY_EMOJI = {
    '餐饮': '🍜', '交通': '🚌', '购物': '🛍️', '娱乐': '🎮',
    '医疗': '🏥', '教育': '📚', '住房': '🏠', '工资': '💰',
    '其他': '💳', '收入': '💵',
}


def add(user_id: str, amount: float, category: str, desc: str,
        rec_type: str = 'expense') -> str:
    """添加财务记录"""
    if not amount or amount <= 0:
        return "💳 请告诉我金额，例如：今天午饭花了 25 元"

    entry = storage.add_finance_record(user_id, amount, category, desc, rec_type)
    emoji = CATEGORY_EMOJI.get(category, '💳')
    type_str = '支出' if rec_type == 'expense' else '收入'
    return f"{emoji} 已记录{type_str}：{desc}\n金额：¥{amount:.2f}\n分类：{category}"


def query(user_id: str, month: str = None) -> str:
    """查询财务摘要"""
    if not month:
        month = date.today().strftime('%Y-%m')
    summary = storage.get_finance_summary(user_id, month)
    records = summary.get('records', [])

    if not records:
        return f"💳 {month} 还没有收支记录"

    lines = [
        f"💰 {month} 收支报告",
        f"总收入：¥{summary['income']:.2f}",
        f"总支出：¥{summary['expense']:.2f}",
        f"结余：¥{summary['balance']:.2f}",
        "\n最近 5 笔记录："
    ]
    for r in sorted(records, key=lambda x: x.get('time', ''), reverse=True)[:5]:
        emoji = '⬆️' if r['type'] == 'income' else '⬇️'
        category_e = CATEGORY_EMOJI.get(r.get('category', ''), '💳')
        lines.append(
            f"  {emoji}{category_e} {r.get('desc', '')} ¥{r.get('amount', 0):.2f}"
        )

    return '\n'.join(lines)
