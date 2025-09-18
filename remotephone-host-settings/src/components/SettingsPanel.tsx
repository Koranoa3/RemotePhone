import React, { useEffect, useState } from 'react';
import { getSettings, setSettings } from '../api/hostApi';

const SettingsPanel: React.FC = () => {
    const [settings, setSettingsState] = useState<any>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const response = await getSettings();
                setSettingsState(response);
            } catch (err) {
                setError('Failed to load settings');
            } finally {
                setLoading(false);
            }
        };

        fetchSettings();
    }, []);

    const handleChange = (key: string, value: any) => {
        setSettingsState((prev: any) => ({
            ...prev,
            [key]: value,
        }));
    };

    const handleSave = async () => {
        try {
            await setSettings(settings);
            alert('Settings saved successfully');
        } catch (err) {
            setError('Failed to save settings');
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>{error}</div>;
    }

    return (
        <div>
            <h2>Settings</h2>
            <div>
                {Object.keys(settings).map((key) => (
                    <div key={key}>
                        <label>
                            {key}:
                            <input
                                type="text"
                                value={settings[key]}
                                onChange={(e) => handleChange(key, e.target.value)}
                            />
                        </label>
                    </div>
                ))}
            </div>
            <button onClick={handleSave}>Save Settings</button>
        </div>
    );
};

export default SettingsPanel;