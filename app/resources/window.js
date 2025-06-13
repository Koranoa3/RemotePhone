const SERVER_URL = "http://skyboxx.tplinkdns.com:8000";
const LATEST_API_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/latest";

window.addEventListener('pywebviewready', async function () {
    console.log('initializing app...');
    // --- ホーム画面のデータ取得 ---
    async function updateHomeStatus() {
        // デバイス接続状態
        const device = await pywebview.api.home.get_device_connection_status();
        if (device.status === 'connected') {
            document.getElementById('disconnected-state').style.display = 'none';
            document.getElementById('connected-state').style.display = 'block';
            document.querySelector('#connected-state .device-name').textContent = device.device_name;
            document.querySelector('#connected-state .rtt-value').textContent = device.rtt;
            document.querySelector('#connected-state .connection-time').textContent = `接続時間: ${device.since}`;

            const rttElem = document.querySelector('#connected-state .rtt-value');
            rttElem.classList.remove('stable', 'unstable', 'very-unstable');
            if (device.rtt_status === 'stable') {
                rttElem.classList.add('stable');
            } else if (device.rtt_status === 'unstable') {
                rttElem.classList.add('unstable');
            } else if (device.rtt_status === 'very-unstable') {
                rttElem.classList.add('very-unstable');
            }
        } else {
            document.getElementById('disconnected-state').style.display = 'block';
            document.getElementById('connected-state').style.display = 'none';
        }

        // サーバー接続状況
        const server = await pywebview.api.home.get_server_connection_status();
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.server-info .status-text');
        statusDot.className = 'status-dot';
        if (server.status === 'ok') {
            statusDot.classList.add('status-normal');
            statusText.textContent = '正常';
        } else if (server.status === 'warn') {
            statusDot.classList.add('status-warn');
            statusText.textContent = '警告';
        } else {
            statusDot.classList.add('status-critical');
            statusText.textContent = '異常';
        }

        // 接続方法
        const comm = await pywebview.api.home.get_communication_methods();
        document.querySelectorAll('.method-option').forEach(opt => {
            const name = opt.querySelector('.method-name').textContent.toLowerCase();
            opt.classList.remove('selected', 'disabled');
            if (!comm.available.includes(name)) opt.classList.add('disabled');
            if (comm.selected === name) opt.classList.add('selected');
        });
    }

    // 接続方法の選択
    document.querySelectorAll('.method-option').forEach(opt => {
        opt.addEventListener('click', async function () {
            if (this.classList.contains('disabled')) return;
            const name = this.querySelector('.method-name').textContent.toLowerCase();
            await pywebview.api.home.set_prefered_communication_method(name);
            await updateHomeStatus();
        });
    });

    // --- デバイス接続画面 ---
    async function updatePasskey() {
        const res = await pywebview.api.connect.get_current_passkey();
        document.getElementById('large-passkey').textContent = res.passkey;
        document.getElementById('timer-text-large').textContent = `残り ${res.remain}秒`;
        document.getElementById('timer-progress-large').style.width = (res.remain / 30 * 100) + '%';
    }
    setInterval(updatePasskey, 1000);
    updatePasskey();

    async function updateRegisteredDevices() {
        const list = await pywebview.api.connect.get_registered_devices();
        const container = document.querySelector('.device-list');
        container.innerHTML = '';
        list.forEach(dev => {
            const el = document.createElement('div');
            el.className = 'device-item';
            el.innerHTML = `
                <div class="device-info">
                    <div class="device-name">${dev.name}</div>
                    <div class="device-status">${dev.last_connection === 0 ? '接続中' : dev.last_connection + '分前に接続'}</div>
                </div>
                <button class="btn btn-danger btn-small" data-uuid="${dev.uuid}">このデバイスを削除する</button>
            `;
            container.appendChild(el);
        });
        container.querySelectorAll('.btn-danger').forEach(btn => {
            btn.onclick = async function () {
                if (confirm('このデバイスを削除しますか？')) {
                    await pywebview.api.connect.delete_registered_device(this.dataset.uuid);
                    updateRegisteredDevices();
                }
            };
        });
    }

    // --- 設定 ---
    async function updateSettings() {
        // 設定を一括取得
        const settings = await pywebview.api.settings.get_settings();
        // システム
        document.querySelector('input[type=checkbox][name=run_on_startup]').checked = settings.system.run_on_startup;
        document.querySelector('input[type=checkbox][name=show_window_on_start]').checked = settings.system.show_window_on_start;
        // アプリ
        document.querySelector('input[type=checkbox][name=enable_auto_update]').checked = settings.application.enable_auto_update;
        document.querySelector('input[type=checkbox][name=auto_restart_on_error]').checked = settings.application.auto_restart_on_error;
        // 通知
        document.getElementById('notification-master').checked = settings.notification.enable_desktop_notification;
        document.querySelectorAll('.notification-sub')[0].checked = settings.notification.notify_authentication_request;
        document.querySelectorAll('.notification-sub')[1].checked = settings.notification.notify_device_connect;
        document.querySelectorAll('.notification-sub')[2].checked = settings.notification.notify_device_disconnect;
    }
    updateSettings();

    // 設定変更時
    document.querySelectorAll('.toggle-switch input').forEach(input => {
        input.addEventListener('change', async function () {
            // すべての設定値をまとめて取得し、APIに渡す
            await pywebview.api.settings.set_settings({
                system: {
                    run_on_startup: document.querySelector('input[name=run_on_startup]').checked,
                    show_window_on_start: document.querySelector('input[name=show_window_on_start]').checked
                },
                application: {
                    enable_auto_update: document.querySelector('input[name=enable_auto_update]').checked,
                    auto_restart_on_error: document.querySelector('input[name=auto_restart_on_error]').checked
                },
                notification: {
                    enable_desktop_notification: document.getElementById('notification-master').checked,
                    notify_authentication_request: document.querySelectorAll('.notification-sub')[0].checked,
                    notify_device_connect: document.querySelectorAll('.notification-sub')[1].checked,
                    notify_device_disconnect: document.querySelectorAll('.notification-sub')[2].checked
                }
            });
        });
    });

    // --- リリースノート ---
    async function updateCurrentReleaseNotes() {
        // バージョン
        const ver = await pywebview.api.release.get_current_application_version();
        document.querySelector('.current-version').textContent = ver.version;
        // リリースノート
        const current = await pywebview.api.release.get_current_version_info();
        if (current) {
            document.getElementById('current-release-version').textContent = current.version;
            document.getElementById('current-release-date').textContent = current.released_at;
            document.getElementById('current-release-content').innerHTML = marked.parse(current.release_notes);
        }
        // 自動アップデート設定
        const autoUpdateStatus = document.querySelector('input[type=checkbox][name=enable_auto_update]').checked;
        document.getElementById('auto-update-status').textContent = autoUpdateStatus ? '有効' : '無効';
    }

    // 更新確認
    async function checkForUpdates() {
        const result = await pywebview.api.release.check_for_updates();
        if (result.update_available) {
            // 最新の更新情報を画面に反映
            document.getElementById('update-available-version').textContent = result.version;
            document.getElementById('update-available-date').textContent = result.released_at;
            document.getElementById('update-available-content').innerHTML = marked.parse(result.release_notes);
            document.getElementById('update-available-container').style.display = 'block';
        } else {
            document.getElementById('update-available-container').style.display = 'none';
        }
    }
    window.checkForUpdates = checkForUpdates;

    // タブ切り替え時に各セクションのデータ再取得
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function () {
            const section = this.getAttribute('data-section');
            if (section === 'home') updateHomeStatus();
            if (section === 'connect') { updatePasskey(); updateRegisteredDevices(); }
            if (section === 'settings') updateSettings();
            if (section === 'release') { updateCurrentReleaseNotes(); checkForUpdates(); }
        });
    });

    // 初期化
    updateHomeStatus();
});

document.addEventListener('DOMContentLoaded', function () {
    // タブ切り替え機能
    const navItems = document.querySelectorAll('.nav-item');
    const contentSections = document.querySelectorAll('.content-section');

    navItems.forEach(item => {
        item.addEventListener('click', function () {
            const targetSection = this.getAttribute('data-section');

            // アクティブなナビゲーションアイテムを更新
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');

            // アクティブなコンテンツセクションを更新
            contentSections.forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(targetSection).classList.add('active');
        });
    }); window.showSettingsSection = () => {
        navItems.forEach(nav => nav.classList.remove('active'));
        document.querySelector('.nav-item[data-section="settings"]').classList.add('active');
        contentSections.forEach(section => section.classList.remove('active'));
        document.getElementById('settings').classList.add('active');
    }

    window.showConnectSection = () => {
        navItems.forEach(nav => nav.classList.remove('active'));
        document.querySelector('.nav-item[data-section="connect"]').classList.add('active');
        contentSections.forEach(section => section.classList.remove('active'));
        document.getElementById('connect').classList.add('active');
    }
});