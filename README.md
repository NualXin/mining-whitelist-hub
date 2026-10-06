# 🏳️ Universal WhiteList Proxy Hub (OpenClash & Mobile)

Автоматический мульти-источниковый агрегатор и валидатор конфигураций **VLESS Reality**, **Trojan** и **Hysteria 2** для обхода блокировок «Белых Списков» (CIDR / SNI) мобильных операторов РФ.

Оптимизирован для:
* **Роутеров с OpenClash (OpenWrt)**: zero-drop LAN, минимальная нагрузка на CPU, защита от утечек DNS.
* **Смартфонов (Flclash, Karing, Sing-box)**: авто-переключение на самый быстрый сервер, низкий расход батареи.

---

## ⚡ Особенности

1. **Мульти-источники и Mirror Racing:**
   Сбор серверов ведётся одновременно из проверенных баз (`igareck`, `zieng2`, `RKPchannel`, `FLAT447`, `solovyov`, `whoahaow`, `VansFenix`). Если GitHub заблокирован местным провайдером или сотовой вышкой, сборщик автоматически забирает резервные копии через **Fastly jsDelivr**, **GHProxy**, **Сбер GitVerse** и **Codeberg**.
2. **Баланс 200 серверов + Личные VIP-ноды:**
   * ~160 проверенных зарубежных серверов с маскировкой под разрешенные домены.
   * ~40 бронебойных серверов РФ (Яндекс.Облако, VK, CDNVideo, Beeline).
   * Поддержка добавления личных платных серверов (в custom_nodes.txt или через Secret CUSTOM_NODES).
   * Исключает «пинг-штормы» и зависания процессора роутера.
3. **Мгновенный Failover (~1 секунда):**
   * Основная группа `🚀 VIP-Auto-Select` (`url-test`) автоматически держит соединение через самую быструю ноду.
   * Резервная группа `🛡️ Emergency-Fallback` (`fallback`) мгновенно подхватывает трафик и переключает на серверы РФ, если зарубежные ноды недоступны.
4. **Стабильные сетевые соединения:**
   * Поддержка непрерывных TCP/UDP потоков без разрывов сессий.
   * Прямой роутинг для российских белых сервисов (без лишнего шифрования и задержек).
5. **Авто-обновление каждые 2 часа:**
   GitHub Actions автоматически каждые 2 часа собирает свежий список серверов и публикует его в ветку `main`.

---

## 🔗 Готовые ссылки на подписку

### 1. Основная ссылка (Fastly CDN — не блокируется в РФ):
```text
https://fastly.jsdelivr.net/gh/NualXin/mining-whitelist-hub@main/clash.yaml
```

### 2. Резервная ссылка (jsDelivr CDN):
```text
https://cdn.jsdelivr.net/gh/NualXin/mining-whitelist-hub@main/clash.yaml
```

### 3. Резервное зеркало (GHProxy):
```text
https://ghproxy.net/https://raw.githubusercontent.com/NualXin/mining-whitelist-hub/main/clash.yaml
```

---

## 📱 Инструкция по настройке

### 1. В OpenClash (роутер OpenWrt):
1. Зайдите в **LuCI** ➔ **Services** ➔ **OpenClash** ➔ **Config Subscribe**.
2. Добавьте новую подписку, укажите Fastly CDN ссылку.
3. Поставьте галочку **Auto Update** и укажите интервал: **4 часа**.
4. Нажмите **Save & Apply** (Сохранить и применить).

### 2. Во Flclash (Android):
1. Откройте **Flclash** ➔ вкладка **«Профили» (Profiles)** ➔ кнопка **«+»**.
2. Вставьте ссылку на `clash.yaml` (через Fastly CDN).
3. Включите автообновление (Auto Update): **каждые 2 часа**.
4. В **Настройках (Settings)**:
   * Тест задержки (Latency URL): `https://pitbit.com` или `https://ya.ru`.
   * Режим DNS (Enhanced Mode): **Fake-IP**.
   * Режим сети: **TUN Mode** (включить).
5. В списке серверов выберите группу **`🚀 VIP-Auto-Select`**.

### 3. В Karing (iOS / Android):
1. Откройте **Karing** ➔ раздел **«Подписки» (Profiles)** ➔ **«+»** ➔ **«Добавить по ссылке»**.
2. Вставьте Fastly CDN ссылку.
3. Выберите автообновление каждые 2–4 часа.
4. Выберите группу **`🚀 VIP-Auto-Select`** и нажмите «Подключить».

---

## 🚀 Настройка на своём GitHub

1. Репозиторий: `NualXin/mining-whitelist-hub`.
2. Включите права на запись для GitHub Actions:
   * Откройте: **Settings** ➔ **Actions** ➔ **General**.
   * В разделе **Workflow permissions** выберите **Read and write permissions** и нажмите **Save**.
3. Готово! GitHub Actions обновляет `clash.yaml` каждые 2 часа автоматически.
