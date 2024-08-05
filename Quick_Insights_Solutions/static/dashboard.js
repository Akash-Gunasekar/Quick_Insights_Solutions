document.addEventListener('DOMContentLoaded', function() {
    const docXButtonCard = document.getElementById('docXButtonCard');
    const docXButton = document.getElementById('docXButton');
    const queryButtonCard = document.getElementById('queryButtonCard');
    const queryButton = document.getElementById('queryButton');
    const backButton = document.getElementById('backButton');
    const defaultInfo = document.querySelector('.default-info');
    const docxChatContainer = document.getElementById('docxChatContainer');
    const queryChatContainer = document.getElementById('queryChatContainer');
    const processFormDocx = document.getElementById('process-form-docx');
    const leftMenu = document.getElementById('leftMenu');
    const menuToggle = document.getElementById('menuToggle');
    const mainContent = document.getElementById('mainContent');
    const rightContent = document.getElementById('rightContent');

    function showContainer(containerId) {
        docxChatContainer.classList.add('hidden');
        queryChatContainer.classList.add('hidden');
        defaultInfo.style.display = 'none';
        backButton.style.display = 'block';

        document.getElementById(containerId).classList.remove('hidden');
    }

    function hideAllContainers() {
        docxChatContainer.classList.add('hidden');
        queryChatContainer.classList.add('hidden');
        defaultInfo.style.display = 'block';
        backButton.style.display = 'none';
    }

    docXButtonCard.addEventListener('click', function() {
        showContainer('docxChatContainer');
    });

    queryButtonCard.addEventListener('click', function() {
        showContainer('queryChatContainer');
    });

    docXButton.addEventListener('click', function() {
        showContainer('docxChatContainer');
    });

    queryButton.addEventListener('click', function() {
        showContainer('queryChatContainer');
    });

    backButton.addEventListener('click', function() {
        hideAllContainers();
    });

    menuToggle.addEventListener('click', function() {
        leftMenu.classList.toggle('hidden');
        mainContent.classList.toggle('expanded');
        rightContent.classList.toggle('expanded');
    });

    processFormDocx.addEventListener('submit', processRequest);
});

async function processRequest(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData();
    const fileInput = document.getElementById('document');
    const queryInput = document.getElementById('docx-query');
    const statusMessage = document.getElementById('status-message-docx');
    const loadingSpinner = document.getElementById('loading-spinner-docx');
    const chatBox = document.getElementById('docx-chat-box');

    if (!fileInput.files[0]) {
        alert('Please select a file.');
        return;
    }

    if (!queryInput.value) {
        alert('Please enter a query.');
        return;
    }

    statusMessage.classList.remove('hidden');
    statusMessage.textContent = 'Processing request...';
    loadingSpinner.classList.remove('hidden');

    formData.append('document', fileInput.files[0]);
    formData.append('query', queryInput.value);

    try {
        const response = await fetch('http://127.0.0.1:5002/docxinsights', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            chatBox.innerHTML += `<div class="chat-message"><span>Filename:</span> ${result.filename}<br><span>Response:</span> ${result.response}</div>`;
            statusMessage.textContent = 'Request processed successfully.';
        } else {
            chatBox.innerHTML += `<div class="chat-message error"><span>Error:</span> ${result.error}</div>`;
            statusMessage.textContent = 'Error processing request.';
        }
    } catch (error) {
        chatBox.innerHTML += `<div class="chat-message error"><span>Error:</span> ${error.message}</div>`;
        statusMessage.textContent = 'Error processing request.';
    } finally {
        loadingSpinner.classList.add('hidden');
        chatBox.scrollTop = chatBox.scrollHeight;
        queryInput.value = ''; // Clear the input field
    }
}

async function askQuestion() {
    const query = document.getElementById("query-input").value;
    const responseElement = document.getElementById("chat-messages-query");

    if (!query) {
        return;
    }

    // Append user's question to the chat
    const userMessage = document.createElement('div');
    userMessage.classList.add('chat-message-box', 'you');
    userMessage.innerHTML = `
        <div class="message you">
            <div class="content">${query}</div>
        </div>
        <div class="time you">${new Date().toLocaleTimeString()}</div>`;
    responseElement.appendChild(userMessage);
    responseElement.scrollTop = responseElement.scrollHeight;

    // Clear the input
    document.getElementById("query-input").value = "";

    const response = await fetch('http://127.0.0.1:5001/questionanswering', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
    });

    const data = await response.json();

    // Append the model's response to the chat
    const botMessage = document.createElement('div');
    botMessage.classList.add('chat-message-box', 'bot');
    botMessage.innerHTML = `
        <div class="message bot">
            <div class="content">${data.response}</div>
        </div>
        <div class="time bot">${new Date().toLocaleTimeString()}</div>`;
    responseElement.appendChild(botMessage);
    responseElement.scrollTop = responseElement.scrollHeight;
}
