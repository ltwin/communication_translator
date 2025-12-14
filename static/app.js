/**
 * 沟通翻译助手前端逻辑
 *
 * 负责处理用户交互、翻译方向选择、流式响应显示等功能。
 */

// DOM 元素引用
const inputContent = document.getElementById('input-content');
const charCount = document.getElementById('char-count');
const translateBtn = document.getElementById('translate-btn');
const outputArea = document.getElementById('output-area');
const directionInputs = document.querySelectorAll('input[name="direction"]');

// 配置常量
const CONFIG = {
    MIN_LENGTH: 10,
    MAX_LENGTH: 2000,
    API_ENDPOINT: '/api/translate'
};

// 状态管理
let isTranslating = false;
let eventSource = null;

/**
 * 初始化应用
 */
function init() {
    // 绑定事件监听器
    inputContent.addEventListener('input', handleInputChange);
    translateBtn.addEventListener('click', handleTranslate);
    directionInputs.forEach(input => {
        input.addEventListener('change', handleDirectionChange);
    });

    // 初始化字符计数
    updateCharCount();
}

/**
 * 处理输入内容变化
 */
function handleInputChange() {
    updateCharCount();
}

/**
 * 更新字符计数显示
 */
function updateCharCount() {
    const length = inputContent.value.length;
    charCount.textContent = `${length} / ${CONFIG.MAX_LENGTH}`;

    // 超过限制时显示警告
    if (length > CONFIG.MAX_LENGTH * 0.9) {
        charCount.classList.add('warning');
    } else {
        charCount.classList.remove('warning');
    }
}

/**
 * 处理翻译方向变化
 */
function handleDirectionChange(event) {
    const direction = event.target.value;
    console.log('Translation direction changed to:', direction);

    // 更新输入提示
    if (direction === 'product_to_dev') {
        inputContent.placeholder = '请输入产品需求描述（10-2000字符）...';
    } else {
        inputContent.placeholder = '请输入技术方案描述（10-2000字符）...';
    }
}

/**
 * 获取当前选择的翻译方向
 */
function getSelectedDirection() {
    const selected = document.querySelector('input[name="direction"]:checked');
    return selected ? selected.value : 'product_to_dev';
}

/**
 * 验证输入内容
 */
function validateInput() {
    const content = inputContent.value.trim();

    if (!content) {
        showError('请输入需要翻译的内容');
        return false;
    }

    if (content.length < CONFIG.MIN_LENGTH) {
        showError(`输入内容过短，请提供更多上下文（至少 ${CONFIG.MIN_LENGTH} 个字符）`);
        return false;
    }

    if (content.length > CONFIG.MAX_LENGTH) {
        showError(`输入内容过长，请控制在 ${CONFIG.MAX_LENGTH} 个字符以内`);
        return false;
    }

    return true;
}

/**
 * 处理翻译请求
 */
async function handleTranslate() {
    // 验证输入
    if (!validateInput()) {
        return;
    }

    // 防止重复提交
    if (isTranslating) {
        return;
    }

    // 设置翻译状态
    setTranslatingState(true);
    clearOutput();

    const content = inputContent.value.trim();
    const direction = getSelectedDirection();

    try {
        // 发送 POST 请求并使用 EventSource 处理流式响应
        await sendTranslateRequest(content, direction);
    } catch (error) {
        console.error('Translation error:', error);
        showError('翻译请求失败，请稍后重试');
        setTranslatingState(false);
    }
}

/**
 * 发送翻译请求并处理流式响应
 */
async function sendTranslateRequest(content, direction) {
    // 关闭之前的连接
    if (eventSource) {
        eventSource.close();
    }

    // 使用 fetch 发送 POST 请求
    const response = await fetch(CONFIG.API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: content,
            direction: direction
        })
    });

    // 检查响应状态
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // 处理流式响应
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    // 开始显示打字效果
    outputArea.classList.add('typing');
    outputArea.innerHTML = '';

    while (true) {
        const { done, value } = await reader.read();

        if (done) {
            break;
        }

        const chunk = decoder.decode(value, { stream: true });
        processSSEChunk(chunk);
    }
}

/**
 * 处理 SSE 数据块
 */
function processSSEChunk(chunk) {
    // SSE 格式: "data: <content>\n\n"
    const lines = chunk.split('\n');

    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const data = line.slice(6);  // 移除 "data: " 前缀
            handleSSEData(data);
        }
    }
}

/**
 * 处理 SSE 数据内容
 */
function handleSSEData(data) {
    // 处理完成标记
    if (data === '[DONE]') {
        console.log('Translation completed');
        setTranslatingState(false);
        outputArea.classList.remove('typing');
        return;
    }

    // 处理错误标记
    if (data.startsWith('[ERROR]')) {
        const errorMessage = data.slice(8).trim() || '翻译过程中发生错误';
        console.error('Translation error:', errorMessage);
        showError(errorMessage);
        setTranslatingState(false);
        outputArea.classList.remove('typing');
        return;
    }

    // 追加内容到输出区域
    appendOutput(data);
}

/**
 * 追加内容到输出区域
 */
function appendOutput(text) {
    // 移除占位文本
    const placeholder = outputArea.querySelector('.placeholder-text');
    if (placeholder) {
        placeholder.remove();
    }

    // 追加新内容
    outputArea.textContent += text;

    // 滚动到底部
    outputArea.scrollTop = outputArea.scrollHeight;
}

/**
 * 清空输出区域
 */
function clearOutput() {
    outputArea.innerHTML = '';
    outputArea.classList.remove('typing');
}

/**
 * 显示错误信息
 */
function showError(message) {
    outputArea.innerHTML = `<p class="error-text">❌ ${message}</p>`;
    outputArea.classList.remove('typing');
}

/**
 * 设置翻译状态
 */
function setTranslatingState(translating) {
    isTranslating = translating;

    if (translating) {
        translateBtn.disabled = true;
        translateBtn.classList.add('loading');
        translateBtn.textContent = '翻译中...';
        inputContent.disabled = true;
        directionInputs.forEach(input => input.disabled = true);
    } else {
        translateBtn.disabled = false;
        translateBtn.classList.remove('loading');
        translateBtn.textContent = '开始翻译';
        inputContent.disabled = false;
        directionInputs.forEach(input => input.disabled = false);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
