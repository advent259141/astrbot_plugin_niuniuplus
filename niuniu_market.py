import os
import yaml
import time
import math
from typing import Dict, List, Tuple, Any, Optional

class NiuniuMarket:
    """牛牛集市类，管理牛牛的上架、购买、回收等功能"""
    
    def __init__(self, plugin):
        """初始化牛牛集市
        
        Args:
            plugin: NiuniuPlugin实例的引用
        """
        self.plugin = plugin
        # 修改为data目录下的路径，而非插件目录，确保数据不会在更新时被覆盖
        self.market_file = os.path.join('data', 'niuniu_market.yml')
        self.market_data = self._load_market_data()
        
    def _load_market_data(self) -> dict:
        """加载集市数据"""
        if not os.path.exists(self.market_file):
            return {'items': {}, 'next_id': 1}
        
        try:
            with open(self.market_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {'items': {}, 'next_id': 1}
                
            # 确保数据格式正确
            if 'items' not in data:
                data['items'] = {}
            if 'next_id' not in data:
                data['next_id'] = 1
                
            return data
        except Exception as e:
            self.plugin.context.logger.error(f"加载集市数据失败: {str(e)}")
            return {'items': {}, 'next_id': 1}
            
    def _save_market_data(self):
        """保存集市数据"""
        try:
            os.makedirs(os.path.dirname(self.market_file), exist_ok=True)
            with open(self.market_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.market_data, f, allow_unicode=True)
        except Exception as e:
            self.plugin.context.logger.error(f"保存集市数据失败: {str(e)}")
            
    def list_market(self) -> str:
        """查看集市上的牛牛列表"""
        items = self.market_data['items']
        if not items:
            return "🏪 牛牛集市空空如也，快来上架你的牛牛吧！"
            
        result = ["🏪 牛牛集市商品列表："]
        for item_id, item in items.items():
            seller_nickname = self._get_nickname(item['group_id'], item['seller_id']) or "未知用户"
            result.append(
                f"编号: {item_id} | {seller_nickname}的牛牛 | "
                f"长度: {self.plugin.format_length(item['length'])} | "
                f"价格: {item['price']}金币 | "
                f"硬度: {item['hardness']}"
            )
        
        return "\n".join(result)
        
    def _get_nickname(self, group_id: str, user_id: str) -> str:
        """获取用户昵称"""
        group_data = self.plugin.get_group_data(group_id)
        user_data = group_data.get(user_id, {})
        return user_data.get('nickname', '未知用户') if isinstance(user_data, dict) else '未知用户'
        
    def is_listing_allowed(self, group_id: str, user_id: str) -> Tuple[bool, str]:
        """检查用户是否可以上架牛牛
        
        Returns:
            Tuple[bool, str]: (是否允许, 不允许的原因)
        """
        # 检查是否注册
        user_data = self.plugin.get_user_data(group_id, user_id)
        if not user_data:
            return False, "你还没有注册牛牛"
            
        # 检查是否在变性状态
        if self.plugin.shop.is_gender_surgery_active(group_id, user_id):
            return False, "变性状态下无法使用牛牛集市"
            
        # 检查是否有有效的牛牛长度
        if user_data.get('length', 0) <= 0:
            return False, "你的牛牛长度太小，无法上架"
            
        # 检查是否已经有牛牛在集市上
        for item in self.market_data['items'].values():
            if item['seller_id'] == user_id and item['group_id'] == group_id:
                return False, "你已经有牛牛在集市上了"
                
        return True, ""
        
    def list_niuniu(self, group_id: str, user_id: str, price: int) -> Tuple[bool, str]:
        """上架牛牛
        
        Args:
            group_id: 群ID
            user_id: 用户ID
            price: 价格
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果信息)
        """
        allowed, reason = self.is_listing_allowed(group_id, user_id)
        if not allowed:
            return False, reason
            
        # 价格必须为正整数
        if price <= 0:
            return False, "价格必须为正整数"
            
        # 获取用户牛牛数据
        user_data = self.plugin.get_user_data(group_id, user_id)
        nickname = user_data.get('nickname', '未知用户')
        length = user_data.get('length', 0)
        hardness = user_data.get('hardness', 1)
        
        # 生成商品ID
        item_id = str(self.market_data['next_id'])
        self.market_data['next_id'] += 1
        
        # 添加到集市
        self.market_data['items'][item_id] = {
            'seller_id': user_id,
            'group_id': group_id,
            'length': length,
            'hardness': hardness,
            'price': price,
            'time': time.time()
        }
        
        # 清空用户的牛牛长度
        user_data['length'] = 0
        self.plugin._save_niuniu_lengths()
        
        # 保存集市数据
        self._save_market_data()
        
        return True, f"🎉 成功上架牛牛！\n编号: {item_id}\n长度: {self.plugin.format_length(length)}\n价格: {price}金币"
        
    def buy_niuniu(self, group_id: str, buyer_id: str, item_id: str) -> Tuple[bool, str]:
        """购买牛牛
        
        Args:
            group_id: 群ID
            buyer_id: 买家ID
            item_id: 商品ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果信息)
        """
        # 检查商品是否存在
        if item_id not in self.market_data['items']:
            return False, "该商品不存在或已被购买"
            
        item = self.market_data['items'][item_id]
        
        # 检查是否是自己的商品
        if item['seller_id'] == buyer_id and item['group_id'] == group_id:
            return False, "不能购买自己的商品"
            
        # 检查买家是否注册
        buyer_data = self.plugin.get_user_data(group_id, buyer_id)
        if not buyer_data:
            return False, "你还没有注册牛牛"
            
        # 检查买家是否在变性状态
        if self.plugin.shop.is_gender_surgery_active(group_id, buyer_id):
            return False, "变性状态下无法使用牛牛集市"
            
        # 检查买家金币是否足够
        if buyer_data.get('coins', 0) < item['price']:
            return False, f"金币不足，需要{item['price']}金币"
            
        # 获取卖家数据
        seller_group_id = item['group_id']
        seller_id = item['seller_id']
        seller_data = self.plugin.get_user_data(seller_group_id, seller_id)
        
        if not seller_data:
            # 如果找不到卖家数据，可能是卖家已经退群或数据丢失
            return False, "无法完成交易，卖家数据异常"
            
        # 执行交易
        # 买家支付金币
        buyer_data['coins'] -= item['price']
        # 卖家获得金币
        seller_data['coins'] = seller_data.get('coins', 0) + item['price']
        # 买家获得牛牛
        buyer_data['length'] = buyer_data.get('length', 0) + item['length']
        buyer_data['hardness'] = max(buyer_data.get('hardness', 1), item['hardness'])
        
        # 从集市中移除商品
        del self.market_data['items'][item_id]
        
        # 保存数据
        self.plugin._save_niuniu_lengths()
        self._save_market_data()
        
        seller_nickname = self._get_nickname(seller_group_id, seller_id)
        return True, (
            f"🎉 成功购买牛牛！\n"
            f"长度: +{self.plugin.format_length(item['length'])}\n"
            f"硬度: {item['hardness']}\n"
            f"卖家: {seller_nickname}\n"
            f"花费: {item['price']}金币\n"
            f"当前长度: {self.plugin.format_length(buyer_data['length'])}"
        )
        
    def recycle_niuniu(self, group_id: str, user_id: str) -> Tuple[bool, str]:
        """回收牛牛
        
        Args:
            group_id: 群ID
            user_id: 用户ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果信息)
        """
        # 检查用户是否注册
        user_data = self.plugin.get_user_data(group_id, user_id)
        if not user_data:
            return False, "你还没有注册牛牛"
            
        # 检查是否在变性状态
        if self.plugin.shop.is_gender_surgery_active(group_id, user_id):
            return False, "变性状态下无法使用牛牛集市"
            
        # 检查牛牛长度
        length = user_data.get('length', 0)
        if length <= 0:
            return False, "你没有可回收的牛牛"
            
        # 计算回收金币(每20cm可以回收1金币，向上取整)
        coins = math.ceil(length / 20)
        
        # 更新用户数据
        user_data['coins'] = user_data.get('coins', 0) + coins
        user_data['length'] = 0
        
        # 保存数据
        self.plugin._save_niuniu_lengths()
        
        return True, f"🔄 成功回收牛牛！\n长度: {self.plugin.format_length(length)}\n获得金币: {coins}\n当前金币: {user_data['coins']}"
        
    def show_market_menu(self) -> str:
        """显示集市菜单"""
        menu = [
            "🏪 牛牛集市功能菜单：",
            "📌 上架牛牛 [价格] - 将你的牛牛上架到集市",
            "📋 查看集市 - 查看所有在售的牛牛",
            "💰 购买牛牛 [编号] - 购买集市上的牛牛",
            "♻️ 回收牛牛 - 直接回收自己的牛牛（每20cm=1金币）",
            "",
            "⚠️ 注意：变性状态下无法使用牛牛集市",
            "⚠️ 上架或回收牛牛后，你的牛牛长度将变为0"
        ]
        return "\n".join(menu)

    # 添加计算可回收金币的预览方法
    def calculate_recycle_coins(self, length: float) -> int:
        """计算回收指定长度牛牛能获得的金币数量"""
        return math.ceil(length / 20)

    async def process_market_command(self, event):
        """处理集市相关命令"""
        group_id = str(event.message_obj.group_id)
        user_id = str(event.get_sender_id())
        nickname = event.get_sender_name()
        msg = event.message_str.strip()
        
        # 检查插件是否启用
        group_data = self.plugin.get_group_data(group_id)
        if not group_data.get('plugin_enabled', False):
            yield event.plain_result("❌ 插件未启用")
            return
            
        # 检查用户是否在打工中
        if self.plugin._is_user_working(group_id, user_id):
            yield event.plain_result(f"小南娘：{nickname}，服务的时候要认真哦！")
            return
            
        # 处理各种命令
        if msg == "牛牛集市":
            yield event.plain_result(self.show_market_menu())
            
        elif msg == "查看集市":
            result = self.list_market()
            yield event.plain_result(result)
            
        elif msg.startswith("上架牛牛"):
            # 解析价格
            try:
                price = int(msg.replace("上架牛牛", "").strip())
            except ValueError:
                yield event.plain_result("❌ 请输入正确的价格，例如：上架牛牛 100")
                return
                
            success, result = self.list_niuniu(group_id, user_id, price)
            yield event.plain_result(result)
            
        elif msg.startswith("购买牛牛"):
            # 解析商品ID
            try:
                item_id = msg.replace("购买牛牛", "").strip()
            except ValueError:
                yield event.plain_result("❌ 请输入正确的商品编号，例如：购买牛牛 1")
                return
                
            success, result = self.buy_niuniu(group_id, user_id, item_id)
            yield event.plain_result(result)
            
        elif msg == "回收牛牛":
            # 先获取用户数据，显示预览信息
            user_data = self.plugin.get_user_data(group_id, user_id)
            if not user_data:
                yield event.plain_result("❌ 你还没有注册牛牛")
                return
                
            length = user_data.get('length', 0)
            if length <= 0:
                yield event.plain_result("❌ 你没有可回收的牛牛")
                return
                
            # 计算可获得的金币
            coins = self.calculate_recycle_coins(length)
            
            # 先显示预览信息
            preview_msg = (
                f"📊 回收预览:\n"
                f"牛牛长度: {self.plugin.format_length(length)}\n"
                f"预计可得: {coins}金币\n\n"
                f"确认回收请回复「确认回收」"
            )
            yield event.plain_result(preview_msg)
            
            # 等待用户确认
            try:
                confirm_event = await self.plugin.wait_for_message(
                    event,
                    lambda e: e.message_str.strip() == "确认回收",
                    timeout=30
                )
                # 用户确认，执行回收
                success, result = self.recycle_niuniu(group_id, user_id)
                yield event.plain_result(result)
            except TimeoutError:
                yield event.plain_result("❌ 回收操作已取消")
