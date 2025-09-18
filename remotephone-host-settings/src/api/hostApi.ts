import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000/api'; // Adjust the base URL as needed

export const getSettings = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/settings`);
        return response.data;
    } catch (error) {
        console.error('Error fetching settings:', error);
        throw error;
    }
};

export const updateSettings = async (settings) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/settings`, settings);
        return response.data;
    } catch (error) {
        console.error('Error updating settings:', error);
        throw error;
    }
};

export const getRegisteredDevices = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/devices`);
        return response.data;
    } catch (error) {
        console.error('Error fetching registered devices:', error);
        throw error;
    }
};

export const deleteRegisteredDevice = async (uuid) => {
    try {
        const response = await axios.delete(`${API_BASE_URL}/devices/${uuid}`);
        return response.data;
    } catch (error) {
        console.error('Error deleting registered device:', error);
        throw error;
    }
};