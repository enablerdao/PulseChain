# PulseChain

> **开发进度**: 实现阶段 | 核心功能和Web界面开发中 | 28个Python文件 | 最后更新: 2025年3月
> 
> PulseChain处于实现阶段，已实现核心区块链功能、环境同步共识和零能耗节点优化。Web界面和API服务器也在开发中。

**本项目是[Enabler株式会社](https://enablerhq.com)的实验性区块链项目。**

[日本語](README.md) | [English](README.en.md) | [한국어](README.ko.md)

```
 ____        _          ____ _           _       
|  _ \ _   _| |___  ___/ ___| |__   __ _(_)_ __  
| |_) | | | | / __|/ _ \ |   | '_ \ / _` | | '_ \ 
|  __/| |_| | \__ \  __/ |___| | | | (_| | | | | |
|_|    \__,_|_|___/\___|\____|_| |_|\__,_|_|_| |_|
                                                  
```

PulseChain是一个全新的第一层区块链，超越了传统的三难困境（去中心化、可扩展性、安全性），专注于实时处理、环境集成和以人为本的设计。它重新定义了区块链的概念，构建了一个可持续的、以人为中心的去中心化生态系统。

## 主要技术特点

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ 实时处理 (RTCS)         │      │ 环境同步共识            │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ 零能耗节点              │      │ 人类信任形成系统        │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ 动态微链                │      │ 后量子密码学            │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

1. **实时交易处理（RTCS：实时共识流）**
   - 放弃区块的概念，实时处理每个交易
   - 网络节点立即验证和批准交易有效性，交易即时完成

2. **环境同步共识机制**
   - 基于环境数据使用VRF（可验证随机函数）选择领导者
   - 确保公平性和安全性的新共识算法
   - 利用天气数据、经济指标和互联网流量等公共数据

3. **零能耗节点运营**
   - 通过低功耗设计最大化能源效率
   - 环保且可持续的区块链生态系统
   - 通过自适应计算进行动态资源调整

4. **人类信任形成系统（人类信任层）**
   - 基于节点信任分数的协作网络形成
   - 实时排除恶意节点
   - 基于社区投票和行为历史的信任评估

5. **动态微链结构**
   - 根据交易负载动态扩展的网络
   - 始终保持最佳性能
   - 临时且动态地生成和消失的微链

6. **后量子密码学**
   - 保护网络免受量子计算机攻击
   - 采用CRYSTALS-Dilithium等抗量子密码学
   - 确保长期安全

## 项目结构

```
PulseChain/
├── pulsechain/             # 核心库
│   ├── core/               # 核心功能
│   │   ├── node.py                # 节点类
│   │   ├── transaction.py         # 交易类
│   │   ├── transaction_pool.py    # 交易池
│   │   ├── trust_system.py        # 人类信任形成系统
│   │   └── microchain.py          # 动态微链
│   ├── consensus/          # 共识机制
│   │   └── environmental.py       # 环境同步共识
│   ├── network/            # 网络通信
│   │   ├── api_server.py          # API服务器
│   │   └── browser_data_collector.py  # 浏览器数据收集
│   ├── crypto/             # 密码学功能
│   │   ├── signatures.py          # 签名功能
│   │   └── post_quantum.py        # 后量子密码学
│   └── utils/              # 工具
│       ├── vrf.py                 # 可验证随机函数
│       ├── weather_api.py         # 天气API集成
│       ├── distributed_data_source.py  # 分布式数据源
│       └── energy_optimizer.py    # 能源优化
├── web/                    # Web界面
│   ├── src/                # React源代码
│   │   ├── components/     # 通用组件
│   │   ├── pages/          # 页面组件
│   │   └── ...
│   ├── public/             # 静态文件
│   └── ...
├── main.py                 # 基本节点执行脚本
├── enhanced_main.py        # 具有扩展功能的节点执行脚本
├── zero_energy_main.py     # 零能耗优化节点执行脚本
└── advanced_pulsechain.py  # 集成所有功能的节点执行脚本
```

## 安装方法

### 后端 (Python)

```bash
# 安装所需包
pip install cryptography pycryptodome fastapi uvicorn asyncio psutil requests
```

### 前端 (React)

```bash
# 导航到web目录
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 使用方法

### 后端

```bash
# 启动基本节点
python main.py --port 52964

# 启动零能耗节点
python zero_energy_main.py --port 52964 --target-cpu-usage 30.0

# 启动高级节点（启用所有功能）
python advanced_pulsechain.py --port 52964
```

### 前端

```bash
# 导航到web目录
cd web

# 启动开发服务器
npm run dev
```

## 许可证

MIT

## 路线图

```
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ 阶段1: 核心开发     │ ──> │ 阶段2: 测试网       │ ──> │ 阶段3: 主网         │
│ 2025年Q1-Q2        │     │ 2025年Q3-Q4        │     │ 2026年Q1-Q2        │
└────────────────────┘     └────────────────────┘     └────────────────────┘
```

- **阶段1**: 核心协议开发、环境同步共识实现、零能耗节点优化
- **阶段2**: 测试网发布、错误修复、安全审计、社区建设
- **阶段3**: 主网启动、生态系统扩展、合作伙伴关系建立

## 社区和贡献

- **Discord**: [PulseChain社区](https://discord.gg/pulsechain)
- **Twitter**: [@PulseChain](https://twitter.com/PulseChain)
- **开发者文档**: [docs.pulsechain.org](https://docs.pulsechain.org)

## 相关项目

查看Enabler株式会社开发的其他区块链项目：

- [NovaLedger](https://github.com/enablerdao/NovaLedger) - 具有超高速处理、高可扩展性、量子抗性和AI优化的下一代区块链技术
- [NexaCore](https://github.com/enablerdao/NexaCore) - 具有AI集成、分片和zk-SNARKs的下一代区块链平台
- [OptimaChain](https://github.com/enablerdao/OptimaChain) - 集成创新扩展技术和高级安全性的分布式区块链平台
- [NeuraChain](https://github.com/enablerdao/NeuraChain) - 集成AI、量子抗性、可扩展性、完全去中心化和能源效率的下一代区块链