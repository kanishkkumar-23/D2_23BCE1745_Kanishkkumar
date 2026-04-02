const { app, BrowserWindow, Menu, ipcMain, shell } = require('electron');
const path = require('path');


class QuMailApp {
    constructor() {
        this.mainWindow = null;
        this.loginWindow = null;
        this.isDevelopment = process.env.NODE_ENV === 'development';
        this.userCredentials = null;
    }

    createMainWindow() {
        // Create the main application window
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1200,
            minHeight: 800,
            show: false, // Don't show until ready
            icon: path.join(__dirname, 'assets', 'icon.png'),
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                enableRemoteModule: true,
                webSecurity: false // For development only
            },
            titleBarStyle: 'default',
            frame: true,
            backgroundColor: '#1a1b2e', // Dark purple background
            vibrancy: 'under-window' // For glassmorphism effect on supported systems
        });

        // Load the main HTML file
        this.mainWindow.loadFile(path.join(__dirname, 'index.html'));
        
        // Pass credentials to main window
        this.mainWindow.webContents.once('dom-ready', () => {
            if (this.userCredentials) {
                this.mainWindow.webContents.send('user-credentials', this.userCredentials);
            }
        });

        // Show window when ready
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            
            // Focus the window
            if (this.isDevelopment) {
                this.mainWindow.webContents.openDevTools();
            }
        });

        // Handle window closed
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        // Handle window maximize/unmaximize for UI adjustments
        this.mainWindow.on('maximize', () => {
            this.mainWindow.webContents.send('window-maximized');
        });

        this.mainWindow.on('unmaximize', () => {
            this.mainWindow.webContents.send('window-unmaximized');
        });
    }

    createLoginWindow() {
        // Create the login window
        this.loginWindow = new BrowserWindow({
            width: 500,
            height: 700,
            resizable: false,
            show: false,
            center: true,
            icon: path.join(__dirname, 'assets', 'icon.png'),
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                enableRemoteModule: true,
                webSecurity: false
            },
            titleBarStyle: 'default',
            frame: true,
            backgroundColor: '#667eea',
            alwaysOnTop: false
        });

        // Load the login HTML file
        this.loginWindow.loadFile(path.join(__dirname, 'login.html'));

        // Show window when ready
        this.loginWindow.once('ready-to-show', () => {
            this.loginWindow.show();
            
            if (this.isDevelopment) {
                this.loginWindow.webContents.openDevTools();
            }
        });

        // Handle window closed
        this.loginWindow.on('closed', () => {
            this.loginWindow = null;
            // If login window is closed without login, quit app
            if (!this.mainWindow) {
                app.quit();
            }
        });
    }

    createMenu() {
        const template = [
            {
                label: 'QuMail',
                submenu: [
                    {
                        label: 'About QuMail',
                        click: () => {
                            this.showAboutDialog();
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Preferences...',
                        accelerator: 'CmdOrCtrl+,',
                        click: () => {
                            this.mainWindow.webContents.send('open-preferences');
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Quit QuMail',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => {
                            app.quit();
                        }
                    }
                ]
            },
            {
                label: 'Email',
                submenu: [
                    {
                        label: 'New Email',
                        accelerator: 'CmdOrCtrl+N',
                        click: () => {
                            this.mainWindow.webContents.send('new-email');
                        }
                    },
                    {
                        label: 'Send Email',
                        accelerator: 'CmdOrCtrl+Enter',
                        click: () => {
                            this.mainWindow.webContents.send('send-email');
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Refresh Inbox',
                        accelerator: 'CmdOrCtrl+R',
                        click: () => {
                            this.mainWindow.webContents.send('refresh-inbox');
                        }
                    }
                ]
            },
            {
                label: 'Security',
                submenu: [
                    {
                        label: 'Level 1: Quantum Secure',
                        click: () => {
                            this.mainWindow.webContents.send('set-encryption-level', 1);
                        }
                    },
                    {
                        label: 'Level 2: Quantum-aided AES',
                        click: () => {
                            this.mainWindow.webContents.send('set-encryption-level', 2);
                        }
                    },
                    {
                        label: 'Level 3: Hybrid PQC',
                        click: () => {
                            this.mainWindow.webContents.send('set-encryption-level', 3);
                        }
                    },
                    {
                        label: 'Level 4: No Quantum Security',
                        click: () => {
                            this.mainWindow.webContents.send('set-encryption-level', 4);
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Quantum Network Status',
                        click: () => {
                            this.mainWindow.webContents.send('show-quantum-network');
                        }
                    }
                ]
            },
            {
                label: 'View',
                submenu: [
                    { role: 'reload' },
                    { role: 'forcereload' },
                    { role: 'toggledevtools' },
                    { type: 'separator' },
                    { role: 'resetzoom' },
                    { role: 'zoomin' },
                    { role: 'zoomout' },
                    { type: 'separator' },
                    { role: 'togglefullscreen' }
                ]
            },
            {
                label: 'Window',
                submenu: [
                    { role: 'minimize' },
                    { role: 'close' }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    showAboutDialog() {
        const { dialog } = require('electron');
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'About QuMail',
            message: 'QuMail: Quantum Secure Email Client',
            detail: `Version: 1.0.0
Developed for ISRO Smart India Hackathon 2025
Problem Statement ID: 25179

Features:
• Quantum Key Distribution (QKD) Integration
• Post-Quantum Cryptography (ML-KEM-768, ML-DSA-6x5)
• Hybrid Encryption Framework (192-bit security)
• Gmail/Yahoo Compatibility
• Violet/Purple Glassmorphism UI

Team: QuMail Team SIH2025`,
            buttons: ['OK']
        });
    }

    setupIPC() {
        // Handle login success
        ipcMain.on('login-success', (event, credentials) => {
            console.log(' Login successful for:', credentials.email);
            this.userCredentials = credentials;
            
            // Close login window
            if (this.loginWindow) {
                this.loginWindow.close();
                this.loginWindow = null;
            }
            
            // Create main window
            this.createMainWindow();
        });

        // Handle external URL opening
        ipcMain.on('open-external-url', (event, url) => {
            shell.openExternal(url);
        });

        // Handle IPC messages from renderer process
        ipcMain.handle('get-app-version', () => {
            return app.getVersion();
        });

        ipcMain.handle('show-save-dialog', async () => {
            const { dialog } = require('electron');
            const result = await dialog.showSaveDialog(this.mainWindow, {
                filters: [
                    { name: 'Email Files', extensions: ['eml'] },
                    { name: 'All Files', extensions: ['*'] }
                ]
            });
            return result;
        });

        ipcMain.handle('show-open-dialog', async () => {
            const { dialog } = require('electron');
            const result = await dialog.showOpenDialog(this.mainWindow, {
                properties: ['openFile', 'multiSelections'],
                filters: [
                    { name: 'All Files', extensions: ['*'] },
                    { name: 'Images', extensions: ['jpg', 'png', 'gif'] },
                    { name: 'Documents', extensions: ['pdf', 'doc', 'docx'] }
                ]
            });
            return result;
        });
    }

    initialize() {
        // Handle app ready
        app.whenReady().then(() => {
            // Start with login window instead of main window
            this.createLoginWindow();
            this.createMenu();
            this.setupIPC();

            // macOS specific: Re-create window when dock icon is clicked
            app.on('activate', () => {
                if (BrowserWindow.getAllWindows().length === 0) {
                    this.createMainWindow();
                }
            });
        });

        // Handle all windows closed
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });

        // Security: Prevent new window creation
        app.on('web-contents-created', (event, contents) => {
            contents.on('new-window', (event, navigationUrl) => {
                event.preventDefault();
                console.log('Blocked new window to:', navigationUrl);
            });
        });
    }
}

// Initialize QuMail application
const quMailApp = new QuMailApp();
quMailApp.initialize();
