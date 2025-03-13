// PulseChain固有のJavaScript機能

document.addEventListener('DOMContentLoaded', function() {
    // 特徴セクションのアニメーション
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach((card, index) => {
        card.classList.add('scroll-reveal');
        card.style.transitionDelay = `${index * 0.1}s`;
    });
    
    // ロードマップのアニメーション
    const roadmapItems = document.querySelectorAll('.roadmap-item');
    
    roadmapItems.forEach((item) => {
        item.classList.add('scroll-reveal');
    });
    
    // ハートビートプロトコルのアニメーション要素を追加
    const heartbeatFeature = document.querySelector('h3:contains("ハートビートプロトコル")');
    
    if (heartbeatFeature) {
        const featureCard = heartbeatFeature.closest('.feature-card');
        
        if (featureCard) {
            const pulseElement = document.createElement('div');
            pulseElement.className = 'pulse-animation mt-4 h-10 w-full relative';
            
            featureCard.appendChild(pulseElement);
        }
    }
    
    // 環境同期型PoHのインタラクティブな説明
    const pohSection = document.querySelector('#technology');
    
    if (pohSection) {
        const pohTitle = pohSection.querySelector('h3:contains("環境同期型PoH")');
        
        if (pohTitle) {
            const demoButton = document.createElement('button');
            demoButton.textContent = 'PoHデモを見る';
            demoButton.className = 'bg-red-600 hover:bg-red-500 text-white rounded px-4 py-2 ml-4 text-sm focus:outline-none';
            
            pohTitle.appendChild(demoButton);
            
            demoButton.addEventListener('click', function() {
                // PoHデモのモーダルを表示
                const modal = document.createElement('div');
                modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
                modal.innerHTML = `
                    <div class="bg-gray-800 p-6 rounded-lg max-w-2xl w-full">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-xl font-bold">PulseChain 環境同期型PoHデモ</h3>
                            <button class="text-gray-400 hover:text-white focus:outline-none" id="close-modal">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <div class="mb-4">
                            <p class="text-gray-300 mb-4">このデモでは、環境データを活用したProof of Historyコンセンサスの動作を示しています。</p>
                            <div class="bg-gray-900 p-4 rounded">
                                <div class="flex justify-between mb-3">
                                    <div>
                                        <div class="text-red-400 text-sm mb-1">PoHシーケンス生成</div>
                                        <div class="text-xl font-mono">0x7a3b...f921</div>
                                    </div>
                                    <div>
                                        <div class="text-red-400 text-sm mb-1">環境データハッシュ</div>
                                        <div class="text-xl font-mono">0x2c9d...e104</div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="text-red-400 text-sm mb-1">ブロック生成進捗</div>
                                    <div class="w-full bg-gray-700 rounded-full h-2.5">
                                        <div class="bg-red-600 h-2.5 rounded-full animate-pulse" style="width: 75%"></div>
                                    </div>
                                </div>
                                <pre class="text-green-400 text-sm overflow-x-auto">
// 環境同期型PoHデモ
Collecting environmental data...
Market data: BTC/USD = 65,432.10
Network state: 1,245 active nodes
Weather data: Tokyo = 22°C, New York = 18°C
Generating PoH sequence...
Verifying with environmental hash...
Block #87654 confirmed in 3.2ms
                                </pre>
                            </div>
                        </div>
                        <div class="text-right">
                            <button class="bg-red-600 hover:bg-red-500 text-white rounded px-4 py-2 focus:outline-none" id="close-demo">閉じる</button>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                
                document.getElementById('close-modal').addEventListener('click', function() {
                    document.body.removeChild(modal);
                });
                
                document.getElementById('close-demo').addEventListener('click', function() {
                    document.body.removeChild(modal);
                });
            });
        }
    }
});