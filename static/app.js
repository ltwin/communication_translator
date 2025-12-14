/**
 * 沟通翻译助手前端逻辑
 *
 * 负责处理用户交互、翻译方向选择、流式响应显示、主题切换等功能。
 */

// DOM 元素引用
const inputContent = document.getElementById('input-content');
const charCount = document.getElementById('char-count');
const translateBtn = document.getElementById('translate-btn');
const outputArea = document.getElementById('output-area');
const directionSelect = document.getElementById('direction-select');
const copyBtn = document.getElementById('copy-btn');
const themeToggle = document.getElementById('theme-toggle');

// 配置常量
const CONFIG = {
    MIN_LENGTH: 10,
    MAX_LENGTH: 2000,
    API_ENDPOINT: '/api/translate'
};

// 状态管理
let isTranslating = false;
let eventSource = null;
let outputBuffer = '';  // 累积流式输出内容用于 Markdown 渲染

/**
 * 初始化应用
 */
function init() {
    // 绑定事件监听器
    inputContent.addEventListener('input', handleInputChange);
    translateBtn.addEventListener('click', handleTranslate);
    directionSelect.addEventListener('change', handleDirectionChange);
    copyBtn.addEventListener('click', handleCopyResult);
    themeToggle.addEventListener('click', toggleTheme);

    // 初始化字符计数
    updateCharCount();

    // 初始化主题按钮文字
    updateThemeToggleText();
}

/**
 * 获取当前主题
 */
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
}

/**
 * 切换主题
 */
function toggleTheme() {
    const current = getCurrentTheme();
    const next = current === 'light' ? 'dark' : 'light';

    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeToggleText();
}

/**
 * 更新主题切换按钮文字
 */
function updateThemeToggleText() {
    const current = getCurrentTheme();
    const icon = themeToggle.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = current === 'light' ? '暗色' : '亮色';
    }
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
function handleDirectionChange() {
    const direction = directionSelect.value;
    console.log('Translation direction changed to:', direction);

    // 更新输入提示
    if (direction === 'auto') {
        inputContent.placeholder = '请输入内容，系统将自动识别类型（10-2000字符）...';
    } else if (direction === 'product_to_dev') {
        inputContent.placeholder = '请输入产品需求描述（10-2000字符）...';
    } else {
        inputContent.placeholder = '请输入技术方案描述（10-2000字符）...';
    }
}

/**
 * 获取当前选择的翻译方向
 * @returns {string|null} 翻译方向，智能模式时返回 null
 */
function getSelectedDirection() {
    const value = directionSelect.value;
    return value === 'auto' ? null : value;
}

/**
 * 判断是否为智能模式
 */
function isAutoDetectMode() {
    return directionSelect.value === 'auto';
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

    // 构建请求体
    const autoDetect = isAutoDetectMode();
    const requestBody = {
        content: content,
        auto_detect: autoDetect
    };

    // 仅在手动模式时设置 direction
    if (!autoDetect && direction) {
        requestBody.direction = direction;
    }

    // 使用 fetch 发送 POST 请求
    const response = await fetch(CONFIG.API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
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
    // 使用正则分割：只在 \n\n 后跟 data: 或字符串结尾处分割
    // 这样可以保留内容中的换行符（如 AI 输出的 \n 不会丢失）
    const messages = chunk.split(/\n\n(?=data: |$)/);

    for (const message of messages) {
        if (message.startsWith('data: ')) {
            const data = message.slice(6);  // 移除 "data: " 前缀
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

    // 处理元数据标记（智能模式）
    if (data.startsWith('[META]')) {
        const metaJson = data.slice(7).trim();
        try {
            const meta = JSON.parse(metaJson);
            displayIntentMeta(meta);
        } catch (e) {
            console.error('Failed to parse META data:', e);
        }
        return;
    }

    // 追加内容到输出区域
    appendOutput(data);
}

/**
 * 显示意图识别元数据
 */
function displayIntentMeta(meta) {
    const directionLabel = meta.detected_direction === 'product_to_dev'
        ? '产品需求 → 技术语言'
        : '技术方案 → 业务语言';

    const confidencePercent = Math.round(meta.confidence * 100);
    const confidenceClass = meta.confidence >= 0.8 ? 'high' : 'medium';

    const metaHtml = `
        <div class="intent-meta">
            <span class="meta-label">智能识别:</span>
            <span class="meta-direction">${directionLabel}</span>
            <span class="meta-confidence ${confidenceClass}">(置信度: ${confidencePercent}%)</span>
        </div>
    `;

    // 移除占位文本
    const placeholder = outputArea.querySelector('.placeholder-text');
    if (placeholder) {
        placeholder.remove();
    }

    // 插入元数据显示
    outputArea.insertAdjacentHTML('beforeend', metaHtml);
}

/**
 * 追加内容到输出区域（使用 Markdown 渲染）
 */
function appendOutput(text) {
    // 移除占位文本
    const placeholder = outputArea.querySelector('.placeholder-text');
    if (placeholder) {
        placeholder.remove();
    }

    // 累积内容到缓冲区
    outputBuffer += text;

    // 使用 marked.js 渲染 Markdown
    outputArea.innerHTML = marked.parse(outputBuffer);

    // 滚动到底部
    outputArea.scrollTop = outputArea.scrollHeight;
}

/**
 * 清空输出区域
 */
function clearOutput() {
    outputBuffer = '';  // 重置 Markdown 缓冲区
    outputArea.innerHTML = '';
    outputArea.classList.remove('typing');
}

/**
 * 显示错误信息
 */
function showError(message) {
    outputArea.innerHTML = `<p class="error-text">${message}</p>`;
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
        directionSelect.disabled = true;
    } else {
        translateBtn.disabled = false;
        translateBtn.classList.remove('loading');
        translateBtn.textContent = '开始翻译';
        inputContent.disabled = false;
        directionSelect.disabled = false;
    }
}

/**
 * 处理复制翻译结果
 */
async function handleCopyResult() {
    // 检查是否有内容可复制
    if (!outputBuffer || outputBuffer.trim() === '') {
        return;
    }

    try {
        // 使用 Clipboard API 复制纯文本
        await navigator.clipboard.writeText(outputBuffer);

        // 显示复制成功状态
        copyBtn.textContent = '已复制';
        copyBtn.classList.add('copied');

        // 2秒后恢复原状
        setTimeout(() => {
            copyBtn.textContent = '复制';
            copyBtn.classList.remove('copied');
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
        // 降级方案：使用 execCommand
        fallbackCopy(outputBuffer);
    }
}

/**
 * 降级复制方案（兼容旧浏览器）
 */
function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.select();

    try {
        document.execCommand('copy');
        copyBtn.textContent = '已复制';
        copyBtn.classList.add('copied');

        setTimeout(() => {
            copyBtn.textContent = '复制';
            copyBtn.classList.remove('copied');
        }, 2000);
    } catch (err) {
        console.error('Fallback copy failed:', err);
    }

    document.body.removeChild(textArea);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
