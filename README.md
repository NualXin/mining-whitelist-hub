# 🏳️ Mining & Mobile Whitelist Proxy Aggregator

Автоматический мульти-источниковый агрегатор и валидатор конфигураций **VLESS Reality**, **Trojan** и **Hysteria 2** для обхода блокировок «Белых Списков» (CIDR / SNI) мобильных операторов РФ.

Оптимизирован для:
* **Асиков и майнинг-роутеров с OpenClash (OpenWrt)**: стабильный Stratum, zero-drop LAN, проверка пинга к пулам.
* **Смартфонов (Flclash, Karing, Sing-box)**: авто-переключение на самый быстрый сервер, низкий расход батареи.

---

## ⚡ Особенности

1. **Мульти-источники и Mirror Racing:**
   Сбор серверов ведётся одновременно из лучших независимых баз (`igareck`, `zieng2`, `RKPchannel`, `FLAT447`, `solovyov`, `whoahaow`, `VansFenix`). Если GitHub заблокирован местным провайдером/вышкой, сборщик автоматически забирает резервные копии через **Fastly jsDelivr**, **GHProxy**, **Сбер GitVerse** и **Codeberg**.
2. **Баланс 150–200 серверов (VIP-кэш):**
   * ~135 быстрых зарубежных серверов с маскировкой под российские домены.
   * ~55 бронебойных серверов РФ (Яндекс.Облако, VK, CDNVideo, Beeline).
   * Исключает «пинг-штормы» и перегрузку процессора роутера.
3. **Мгновенный Failover (~1 секунда):**
   * Основная группа `🚀 VIP-Auto-Select` (`url-test`) автоматически держит соединение через самую быструю ноду.
   * Резервная группа `🛡️ Emergency-Fallback` (`fallback`) мгновенно подхватывает трафик и переключает на серверы РФ, если зарубежные ноды заблокированы.
4. **Защита Stratum-сессий майнинга:**
   * Прямой проброс (`DIRECT`) для портов `3333`, `4433`, `25`, `8000`, `8888`.
   * Прямой роутинг доменов `trustpool.ru`, `trustpool.cc`, `viabtc.com`, `emcd.io`, `pitbit.com` (без лишнего шифрования и накладных расходов).
5. **Авто-обновление каждые 2 часа:**
   GitHub Actions автоматически каждые 2 часа собирает свежий список серверов и публикует его в ветку `main`.

---

## 🔗 Готовые ссылки на подписку

Замените `USERNAME/REPO` на имя вашего репозитория на GitHub:

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

### 1. Во Flclash (Android):
1. Откройте **Flclash** ➔ вкладка **«Профили» (Profiles)** ➔ кнопка **«+»**.
2. Вставьте ссылку на `clash.yaml` (через Fastly CDN).
3. Включите автообновление (Auto Update): **каждые 2 часа**.
4. В **Настройках (Settings)**:
   * Тест задержки (Latency URL): `https://pitbit.com` или `https://ya.ru`.
   * Режим DNS (Enhanced Mode): **Fake-IP**.
   * Режим сети: **TUN Mode** (включить).
5. В списке серверов выберите группу **`🚀 VIP-Auto-Select`**.

### 2. В Karing (iOS / Android):
1. Откройте **Karing** ➔ раздел **«Подписки» (Profiles)** ➔ **«+»** ➔ **«Добавить по ссылке»**.
2. Вставьте Fastly CDN ссылку.
3. Выберите автообновление каждые 2–4 часа.
4. Выберите группу **`🚀 VIP-Auto-Select`** и нажмите «Подключить».

### 3. В OpenClash (роутер OpenWrt):
1. Зайдите в **LuCI** ➔ **Services** ➔ **OpenClash** ➔ **Config Subscribe**.
2. Добавьте новую подписку, укажите Fastly CDN ссылку.
3. Поставьте галочку **Auto Update** и укажите интервал: **4 часа**.
4. Нажмите **Save & Apply** (Сохранить и применить).

---

## 🚀 Как развернуть на своём GitHub

1. Создайте **публичный (Public)** репозиторий на GitHub (например, `mining-whitelist-hub`).
2. Скопируйте файлы проекта в репозиторий:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: whitelist aggregator"
   git branch -M main
   git remote add origin https://github.com/ВАШ_ЛОГИН/mining-whitelist-hub.git
   git push -u origin main
   ```
3. Включите права на запись для GitHub Actions:
   * В репозитории откройте: **Settings** ➔ **Actions** ➔ **General**.
   * Прокрутите до раздела **Workflow permissions**.
   * Выберите **Read and write permissions** и нажмите **Save**.
4. Готово! GitHub Actions начнёт обновлять `clash.yaml` каждые 2 часа автоматически.
