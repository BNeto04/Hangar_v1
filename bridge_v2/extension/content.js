// Hangar V1 — Bridge V2 ChatGPT Inbound Continuous Extension (v2.0.0)
console.log("[Hangar V1 Bridge V2] Extensão ativa em chatgpt.com. Pronta para submissão de CONTEXT_PACKET.");

const STATUS_URL = "http://127.0.0.1:8765/status";
const ACK_URL = "http://127.0.0.1:8765/ack";
const POLL_INTERVAL_MS = 3000;
let lastProcessedMessageId = null;

try {
  lastProcessedMessageId = sessionStorage.getItem("hangar_v2_last_message_id");
} catch (e) {}

async function checkInboundWake() {
  try {
    const response = await fetch(STATUS_URL);
    if (!response.ok) return;
    const data = await response.json();

    if (!data.pending_wake) return;
    if (!data.message_id || data.message_id === lastProcessedMessageId) return;

    console.log(`[Hangar V1 Bridge V2] Novo CONTEXT_PACKET detectado: ${data.message_id} (${data.call_id}). Injetando no ChatGPT...`);

    const packetText = data.text || "";
    if (!packetText.trim()) return;

    const injected = injectPacketIntoPrompt(packetText);
    if (injected) {
      lastProcessedMessageId = data.message_id;
      try {
        sessionStorage.setItem("hangar_v2_last_message_id", lastProcessedMessageId);
      } catch (e) {}

      await fetch(ACK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message_id: data.message_id })
      });
      console.log(`[Hangar V1 Bridge V2] CONTEXT_PACKET injetado e ACK confirmado para ${data.message_id}.`);
    }
  } catch (err) {
    // Silencioso em caso de servidor offline
  }
}

function injectPacketIntoPrompt(textToInject) {
  const promptEl = document.querySelector("#prompt-textarea") || 
                   document.querySelector("div[contenteditable='true']") ||
                   document.querySelector("textarea");
  if (!promptEl) {
    console.warn("[Hangar V1 Bridge V2] Campo de prompt do ChatGPT não encontrado.");
    return false;
  }

  promptEl.focus();
  if (promptEl.tagName === "TEXTAREA") {
    promptEl.value = textToInject;
    promptEl.dispatchEvent(new Event("input", { bubbles: true }));
  } else {
    promptEl.innerText = textToInject;
    promptEl.dispatchEvent(new Event("input", { bubbles: true }));
  }

  setTimeout(() => {
    const sendButton = document.querySelector("button[data-testid='send-button']") || 
                       document.querySelector("button[aria-label='Enviar prompt']") ||
                       document.querySelector("button[aria-label='Send prompt']");
    if (sendButton && !sendButton.disabled) {
      sendButton.click();
      console.log("[Hangar V1 Bridge V2] Botão de envio acionado com sucesso!");
    } else {
      const enterEvent = new KeyboardEvent("keydown", {
        bubbles: true,
        cancelable: true,
        key: "Enter",
        code: "Enter",
        keyCode: 13
      });
      promptEl.dispatchEvent(enterEvent);
      console.log("[Hangar V1 Bridge V2] Evento Enter acionado no prompt.");
    }
  }, 350);

  return true;
}

setInterval(checkInboundWake, POLL_INTERVAL_MS);
