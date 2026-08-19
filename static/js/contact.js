const messageField = document.querySelector("#id_message");
const messageCount = document.querySelector("#message-count");

if (messageField && messageCount) {
    const updateMessageCount = () => {
        messageCount.textContent = `${messageField.value.length} / 3000`;
    };

    messageField.addEventListener("input", updateMessageCount);
    updateMessageCount();
}