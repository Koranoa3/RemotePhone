// This file contains type definitions used throughout the application.

export interface DeviceConnectionStatus {
    status: 'connected' | 'not connected';
    device_name: string;
    rtt: string;
    rtt_status: 'stable' | 'unstable';
    since: string;
}

export interface ServerConnectionStatus {
    status: 'ok' | 'warn' | 'critical';
}

export interface CommunicationMethods {
    available: string[];
    preferred: string;
    selected: string;
}

export interface Passkey {
    key: string;
    remain: number;
}

export interface RegisteredDevice {
    name: string;
    uuid: string;
    last_connection: number;
}

export interface Settings {
    [key: string]: any; // Adjust this type according to your settings structure
}

export interface ApplicationVersion {
    version: string;
}

export interface VersionInfo {
    version: string;
    released_at: string;
    release_notes: string;
}

export interface UpdateCheck {
    update_available: boolean;
    version?: string;
    released_at?: string;
    release_notes?: string;
}