# PulseChain

> **Development Status**: Implementation Stage | Core Features & Web Interface in Development | 28 Python Files | Last Updated: March 2025
> 
> PulseChain is in the implementation stage, with core blockchain functionality, environment-synchronized consensus, and zero-energy node optimization implemented. Web interface and API server are also under development.

**This project is an experimental blockchain project by [Enabler Inc.](https://enablerhq.com)**

[日本語](README.md) | [中文](README.zh-CN.md) | [한국어](README.ko.md)

```
 ____        _          ____ _           _       
|  _ \ _   _| |___  ___/ ___| |__   __ _(_)_ __  
| |_) | | | | / __|/ _ \ |   | '_ \ / _` | | '_ \ 
|  __/| |_| | \__ \  __/ |___| | | | (_| | | | | |
|_|    \__,_|_|___/\___|\____|_| |_|\__,_|_|_| |_|
                                                  
```

PulseChain is a completely new layer-one blockchain that goes beyond the traditional trilemma (decentralization, scalability, security) to focus on real-time processing, environmental integration, and human-centric design. It redefines the concept of blockchain to build a sustainable and human-centered decentralized ecosystem.

## Key Technical Features

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ Real-time Processing    │      │ Environment-Synchronized │ │
│  │ (RTCS)                  │      │ Consensus               │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ Zero-Energy Nodes       │      │ Human Trust Formation   │ │
│  │                         │      │ System                  │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ Dynamic Microchains     │      │ Post-Quantum            │ │
│  │                         │      │ Cryptography            │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

1. **Real-time Transaction Processing (RTCS: Real-time Consensus Stream)**
   - Abandons the concept of blocks, processing each transaction in real-time
   - Network nodes immediately verify and approve transaction validity, completing transactions instantly

2. **Environment-Synchronized Consensus Mechanism**
   - Leader selection using VRF (Verifiable Random Function) based on environmental data
   - A new consensus algorithm ensuring fairness and security
   - Utilizes public data such as weather data, economic indicators, and internet traffic

3. **Zero-Energy Node Operation**
   - Maximizes energy efficiency through low-power design
   - Environmentally friendly and sustainable blockchain ecosystem
   - Dynamic resource adjustment through adaptive computing

4. **Human Trust Formation System (Human Trust Layer)**
   - Cooperative network formation based on node trust scores
   - Real-time exclusion of malicious nodes
   - Trust evaluation based on community voting and behavior history

5. **Dynamic Microchain Structure**
   - Network that dynamically scales according to transaction load
   - Maintains optimal performance at all times
   - Temporary and dynamic generation and disappearance of microchains

6. **Post-Quantum Cryptography**
   - Defends the network against attacks from quantum computers
   - Adopts quantum-resistant cryptography such as CRYSTALS-Dilithium
   - Ensures long-term security

## Project Structure

```
PulseChain/
├── pulsechain/             # Core library
│   ├── core/               # Core functionality
│   │   ├── node.py                # Node class
│   │   ├── transaction.py         # Transaction class
│   │   ├── transaction_pool.py    # Transaction pool
│   │   ├── trust_system.py        # Human trust formation system
│   │   └── microchain.py          # Dynamic microchain
│   ├── consensus/          # Consensus mechanism
│   │   └── environmental.py       # Environment-synchronized consensus
│   ├── network/            # Network communication
│   │   ├── api_server.py          # API server
│   │   └── browser_data_collector.py  # Browser data collection
│   ├── crypto/             # Cryptography functionality
│   │   ├── signatures.py          # Signature functionality
│   │   └── post_quantum.py        # Post-quantum cryptography
│   └── utils/              # Utilities
│       ├── vrf.py                 # Verifiable random function
│       ├── weather_api.py         # Weather API integration
│       ├── distributed_data_source.py  # Distributed data source
│       └── energy_optimizer.py    # Energy optimization
├── web/                    # Web interface
│   ├── src/                # React source code
│   │   ├── components/     # Common components
│   │   ├── pages/          # Page components
│   │   └── ...
│   ├── public/             # Static files
│   └── ...
├── main.py                 # Basic node execution script
├── enhanced_main.py        # Node execution script with extended functionality
├── zero_energy_main.py     # Zero-energy optimized node execution script
└── advanced_pulsechain.py  # Node execution script integrating all features
```

## Installation

### Backend (Python)

```bash
# Install required packages
pip install cryptography pycryptodome fastapi uvicorn asyncio psutil requests
```

### Frontend (React)

```bash
# Navigate to the web directory
cd web

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Usage

### Backend

```bash
# Start a basic node
python main.py --port 52964

# Start a zero-energy node
python zero_energy_main.py --port 52964 --target-cpu-usage 30.0

# Start an advanced node (enable all features)
python advanced_pulsechain.py --port 52964
```

### Frontend

```bash
# Navigate to the web directory
cd web

# Start the development server
npm run dev
```

## License

MIT

## Roadmap

```
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ Phase 1: Core Dev  │ ──> │ Phase 2: Testnet   │ ──> │ Phase 3: Mainnet   │
│ 2025 Q1-Q2         │     │ 2025 Q3-Q4         │     │ 2026 Q1-Q2         │
└────────────────────┘     └────────────────────┘     └────────────────────┘
```

- **Phase 1**: Core protocol development, environment-synchronized consensus implementation, zero-energy node optimization
- **Phase 2**: Testnet release, bug fixes, security audits, community building
- **Phase 3**: Mainnet launch, ecosystem expansion, partnership building

## Community and Contribution

- **Discord**: [PulseChain Community](https://discord.gg/pulsechain)
- **Twitter**: [@PulseChain](https://twitter.com/PulseChain)
- **Developer Documentation**: [docs.pulsechain.org](https://docs.pulsechain.org)

## Related Projects

Check out other blockchain projects developed by Enabler Inc.:

- [NovaLedger](https://github.com/enablerdao/NovaLedger) - Next-generation blockchain technology featuring ultra-high-speed processing, high scalability, quantum resistance, and AI optimization
- [NexaCore](https://github.com/enablerdao/NexaCore) - Next-generation blockchain platform featuring AI integration, sharding, and zk-SNARKs
- [OptimaChain](https://github.com/enablerdao/OptimaChain) - Distributed blockchain platform integrating innovative scaling technology and advanced security
- [NeuraChain](https://github.com/enablerdao/NeuraChain) - Next-generation blockchain integrating AI, quantum resistance, scalability, complete decentralization, and energy efficiency