import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import { createPinia } from "pinia";
import Notifications from "@kyvg/vue3-notification";
import { Buffer } from "buffer";

window.Buffer = Buffer;

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);
app.use(Notifications, { name: "alert" });
app.mount("#app");
