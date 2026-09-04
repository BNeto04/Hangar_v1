// Hangar V1 — ChatGPT Inbound Wake Bridge Content Script (v1.0.0)
console.log("[Hangar V1] Inbound Wake Extension Ativa em chatgpt.com");

const POLL_URL = "http://127.0.0.1:8765/status";
const ACK_URL = "http://127.0.0.1:8765/ack";
const POLL_INTERVAL_MS = 4000;
let lastProcessedMessageId = null;

try {
  lastProcessedMessageId = sessionStorage.getItem("hangar_last_message_id");
} catch (e) {}

async function checkInboundWake() {
  try {
    const response = await fetch(POLL_URL);
    if (!response.ok) return;
    const data = await response.json();

    if (!data.pending_wake) return;
    if (!data.message_id || data.message_id === lastProcessedMessageId) return;

    console.log(`[Hangar V1] Novo RESULT detectado: ${data.message_id} (${data.call_id}). Injetando wake...`);

    const injected = injectWakeMessage(data.text || "v");
    if (injected) {
      lastProcessedMessageId = data.message_id;
      try {
        sessionStorage.setItem("hangar_last_message_id", lastProcessedMessageId);
      } catch (e) {}
      
      await fetch(ACK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message_id: data.message_id })
      });
      console.log(`[Hangar V1] Wake consumido e ACK enviado para ${data.message_id}.`);
    }
  } catch (err) {}
}

function injectWakeMessage(textToInject) {
  const promptTextarea = document.querySelector("#prompt-textarea") || 
                         document.querySelector("div[contenteditable='true']") ||
                         document.querySelector("textarea");
  if (!promptTextarea) {
    console.warn("[Hangar V1] Campo de prompt do ChatGPT não encontrado.");
    return false;
  }

  promptTextarea.focus();
  if (promptTextarea.tagName === "TEXTAREA") {
    promptTextarea.value = textToInject;
    promptTextarea.dispatchEvent(new Event("input", { bubbles: true }));
  } else {
    promptTextarea.innerText = textToInject;
    promptTextarea.dispatchEvent(new Event("input", { bubbles: true }));
  }

  setTimeout(() => {
    const sendButton = document.querySelector("button[data-testid='send-button']") || 
                       document.querySelector("button[aria-label='Enviar prompt']") ||
                       document.querySelector("button[aria-label='Send prompt']");
    if (sendButton && !sendButton.disabled) {
      sendButton.click();
      console.log("[Hangar V1] Botão de envio clicado com sucesso!");
    } else {
      const enterEvent = new KeyboardEvent("keydown", {
        bubbles: true,
        cancelable: true,
        key: "Enter",
        code: "Enter",
        keyCode: 13
      });
      promptTextarea.dispatchEvent(enterEvent);
      console.log("[Hangar V1] Tecla Enter disparada no prompt.");
    }
  }, 400);

  return true;
}

setInterval(checkInboundWake, POLL_INTERVAL_MS);
