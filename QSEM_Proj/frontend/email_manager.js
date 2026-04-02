class QuMailEmailManager {
    constructor() {
        this.currentFolder = 'inbox';
        this.currentEmail = null;
        this.emailIntegration = null;
        this.isLoading = false;
        
        // UI Elements
        this.loadingIndicator = null;
        this.emailListContainer = null;
        this.emailReaderContainer = null;
        this.emailComposerContainer = null;
        this.folderTitle = null;
        this.emailListCount = null;
        this.emailList = null;
        
        console.log('📧 QuMail Email Manager initialized');
    }

    /**
     * Initialize the email manager
     */
    async initialize() {
        console.log('🔄 Initializing QuMail Email Manager...');
        
        // Wait for email integration to be available
        await this.waitForEmailIntegration();
        
        // Get UI elements
        this.getUIElements();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load inbox emails by default in middle column, compose area always visible
        await this.loadFolder('inbox');
        
        console.log('✅ QuMail Email Manager ready');
    }

    /**
     * Wait for email integration to be available
     */
    async waitForEmailIntegration() {
        let attempts = 0;
        const maxAttempts = 50;
        
        while (attempts < maxAttempts) {
            if (window.emailIntegration) {
                // Check if connected to backend
                if (window.emailIntegration.isConnected) {
                    this.emailIntegration = window.emailIntegration;
                    console.log('✅ Email integration connected to backend');
                    
                    // Check if credentials are set
                    if (window.emailIntegration.credentials) {
                        console.log('✅ Email credentials configured');
                        return;
                    } else {
                        console.log('⚠️ Email integration connected but credentials not set');
                        console.log('💡 Please configure Gmail App Password in the settings');
                        // Still return - we can show a message to configure credentials
                        return;
                    }
                } else {
                    console.log(`⏳ Waiting for backend connection... (${attempts + 1}/${maxAttempts})`);
                }
            } else {
                console.log(`⏳ Waiting for email integration module... (${attempts + 1}/${maxAttempts})`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        throw new Error('❌ Email integration not available - Backend may not be running');
    }

    /**
     * Get all UI elements
     */
    getUIElements() {
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.emailListContainer = document.getElementById('email-list-container');
        this.emailReaderContainer = document.getElementById('email-reader-container');
        this.emailComposerContainer = document.getElementById('email-composer-container');
        this.folderTitle = document.getElementById('folder-title');
        this.emailListCount = document.getElementById('email-list-count');
        this.emailList = document.getElementById('email-list');
        
        console.log('📋 UI elements initialized');
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Folder navigation
        document.querySelectorAll('.nav-folder').forEach(folder => {
            folder.addEventListener('click', (e) => {
                e.preventDefault();
                const folderName = folder.dataset.folder;
                this.loadFolder(folderName);
            });
        });

        // Top compose button
        const topComposeBtn = document.getElementById('top-compose-btn');
        if (topComposeBtn) {
            topComposeBtn.addEventListener('click', () => {
                this.showComposer();
            });
        }

        // Sidebar compose button
        const sidebarComposeBtn = document.getElementById('sidebar-compose-btn');
        if (sidebarComposeBtn) {
            sidebarComposeBtn.addEventListener('click', () => {
                this.showComposer();
            });
        }

        // Email reader close button
        const closeEmailReader = document.getElementById('close-email-reader');
        if (closeEmailReader) {
            closeEmailReader.addEventListener('click', () => {
                this.closeEmailReader();
            });
        }

        console.log('🎧 Event listeners setup complete');
    }


    /**
     * Show loading state in middle column
     */
    showLoading() {
        this.loadingIndicator.classList.remove('hidden');
        this.emailListContainer.classList.add('hidden');
        this.isLoading = true;
    }

    /**
     * Show email thumbnails in middle column
     */
    showEmailList() {
        this.loadingIndicator.classList.add('hidden');
        this.emailListContainer.classList.remove('hidden');
        this.isLoading = false;
    }

    /**
     * Show email reader as overlay on top of compose area
     */
    showEmailReader() {
        const overlay = document.getElementById('email-reader-overlay');
        const composeContainer = document.getElementById('email-composer-container');
        
        if (overlay) {
            overlay.classList.remove('hidden');
        }
        
        // Add blur effect to compose area
        if (composeContainer) {
            composeContainer.classList.add('blur-sm', 'opacity-75');
        }
        
        this.isLoading = false;
    }

    /**
     * Show composer (always visible, just close any overlay)
     */
    showComposer() {
        this.closeEmailReader();
        console.log('✍️ Composer focused');
    }

    /**
     * Close email reader overlay (compose area remains visible)
     */
    closeEmailReader() {
        const overlay = document.getElementById('email-reader-overlay');
        const composeContainer = document.getElementById('email-composer-container');
        
        if (overlay) {
            overlay.classList.add('hidden');
        }
        
        // Remove blur effect from compose area
        if (composeContainer) {
            composeContainer.classList.remove('blur-sm', 'opacity-75');
        }
        
        this.currentEmail = null;
        console.log('📪 Email reader closed, compose area restored');
    }

    /**
     * Load emails from a specific folder
     */
    async loadFolder(folderName) {
        console.log(`📁 Loading folder: ${folderName}`);
        
        // Update active folder
        this.updateActiveFolder(folderName);
        this.currentFolder = folderName;
        
        // Show loading
        this.showLoading();
        
        try {
            // Check if email integration is ready
            if (!this.emailIntegration || !this.emailIntegration.isReady()) {
                if (!this.emailIntegration) {
                    throw new Error('Email integration not available');
                } else if (!this.emailIntegration.isConnected) {
                    throw new Error('Backend not connected. Please start the backend server.');
                } else if (!this.emailIntegration.credentials) {
                    this.showCredentialsRequired();
                    return;
                }
            }
            
            // Fetch emails from the specific folder
            let result;
            const limit = 10; // Fetch up to 10 emails
            
            switch (folderName) {
                case 'inbox':
                    result = await this.emailIntegration.getInboxEmails(limit);
                    break;
                case 'sent':
                    try {
                        result = await this.emailIntegration.getSentEmails(limit);
                    } catch (sentError) {
                        console.warn(`⚠️ Sent folder access failed:`, sentError.message);
                        result = { 
                            emails: [], 
                            message: `Sent folder not accessible: ${sentError.message}. This is common with some Gmail configurations. Try accessing the folder directly in Gmail to enable it.` 
                        };
                    }
                    break;
                case 'drafts':
                    try {
                        result = await this.emailIntegration.getDraftEmails(limit);
                    } catch (draftError) {
                        console.warn(`⚠️ Drafts folder access failed:`, draftError.message);
                        result = { 
                            emails: [], 
                            message: `Drafts folder not accessible: ${draftError.message}. This folder may not be enabled for IMAP access.` 
                        };
                    }
                    break;
                case 'trash':
                    try {
                        result = await this.emailIntegration.getTrashEmails(limit);
                    } catch (trashError) {
                        console.warn(`⚠️ Trash folder access failed:`, trashError.message);
                        result = { 
                            emails: [], 
                            message: `Trash folder not accessible: ${trashError.message}. This folder may not be enabled for IMAP access.` 
                        };
                    }
                    break;
                default:
                    result = await this.emailIntegration.getInboxEmails(limit);
            }

            console.log(`📬 Received ${result.emails?.length || 0} emails from ${folderName}`);
            
            // Display emails (even if empty, to show the message)
            this.displayEmails(result.emails || [], folderName, result.message);
            
        } catch (error) {
            console.error(`❌ Error loading ${folderName}:`, error);
            this.showEmailList();
            this.displayError(`Failed to load ${folderName}: ${error.message}`);
        }
    }

    /**
     * Update active folder in UI
     */
    updateActiveFolder(folderName) {
        // Remove active class from all folders
        document.querySelectorAll('.nav-folder').forEach(folder => {
            folder.classList.remove('bg-violet-500/20');
        });
        
        // Add active class to current folder
        const activeFolder = document.querySelector(`[data-folder="${folderName}"]`);
        if (activeFolder) {
            activeFolder.classList.add('bg-violet-500/20');
        }
        
        // Update title
        const folderTitleMap = {
            inbox: 'Inbox',
            sent: 'Sent',
            drafts: 'Drafts',
            trash: 'Trash'
        };
        
        if (this.folderTitle) {
            this.folderTitle.textContent = folderTitleMap[folderName] || 'Unknown';
        }
    }

    /**
     * Display emails in the list
     */
    displayEmails(emails, folderName, message = null) {
        if (!this.emailList || !this.emailListCount) return;
        
        // Update count
        this.emailListCount.textContent = `${emails.length} emails`;
        this.updateFolderCount(folderName, emails.length);
        
        // Clear previous emails
        this.emailList.innerHTML = '';
        
        if (emails.length === 0) {
            const messageText = message || 'This folder is empty';
            this.emailList.innerHTML = `
                <div class="text-center py-8 text-violet-300">
                    <svg class="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                    </svg>
                    <p class="text-sm font-medium">No emails found</p>
                    <p class="text-xs opacity-75">${this.escapeHtml(messageText)}</p>
                </div>
            `;
        } else {
            // Add each email as a clickable item
            emails.forEach((email, index) => {
                const emailItem = this.createEmailItem(email, index);
                this.emailList.appendChild(emailItem);
            });
        }
        
        // Show email list
        this.showEmailList();
        
        console.log(`📋 Displayed ${emails.length} emails for ${folderName}`);
    }

    /**
     * Create an email thumbnail item (like Alice Kumar style in the image)
     */
    createEmailItem(email, index) {
        const emailDiv = document.createElement('div');
        emailDiv.className = 'email-thumbnail p-3 rounded-lg hover:bg-violet-500/10 cursor-pointer transition-all duration-200 border-b border-violet-500/10';
        emailDiv.dataset.emailIndex = index;
        
        // Extract email data with proper field mapping from backend
        const from = email.sender || email.from || 'Unknown Sender';
        const subject = this.decodeUtf8String(email.subject || 'No Subject');
        const snippet = this.getEmailSnippet(email);
        const date = email.received_at ? new Date(email.received_at) : (email.date ? new Date(email.date) : null);
        const isQuMail = email.is_qumail || false;
        
        // Get sender initials for avatar
        const initials = this.getInitials(from);
        
        // Create QuMail level badge or regular indicator
        let levelBadge = '';
        if (isQuMail) {
            const securityLevel = this.getQuMailLevel(email);
            levelBadge = `<span class="text-xs px-2 py-1 rounded-full bg-violet-500/20 text-violet-300">${securityLevel}</span>`;
        } else {
            levelBadge = '<span class="text-xs px-2 py-1 rounded-full bg-gray-500/20 text-gray-400">Regular</span>';
        }
        
        // Format time (like "2m", "15m", "1h")
        const timeAgo = date ? this.formatTimeAgo(date) : '';
        
        // Create green online indicator if recent
        const isRecent = date && (new Date() - date) < 30 * 60 * 1000; // 30 minutes
        const onlineIndicator = isRecent ? '<div class="w-2 h-2 rounded-full bg-green-400 absolute top-1 right-1"></div>' : '';
        
        emailDiv.innerHTML = `
            <div class="flex items-center space-x-3">
                <!-- Avatar with initials -->
                <div class="relative flex-shrink-0">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-r ${this.getAvatarColor(from)} flex items-center justify-center text-white font-medium text-sm">
                        ${initials}
                    </div>
                    ${onlineIndicator}
                </div>
                
                <!-- Email Content -->
                <div class="flex-1 min-w-0">
                    <!-- Sender name and time -->
                    <div class="flex items-center justify-between mb-1">
                        <h3 class="text-white font-medium text-sm truncate">${this.escapeHtml(this.getDisplayName(from))}</h3>
                        <span class="text-gray-400 text-xs">${timeAgo}</span>
                    </div>
                    
                    <!-- Subject -->
                    <h4 class="text-violet-300 text-sm font-medium truncate mb-1">${this.escapeHtml(subject)}</h4>
                    
                    <!-- Snippet -->
                    <p class="text-gray-400 text-xs truncate mb-2">${this.escapeHtml(snippet)}...</p>
                    
                    <!-- Level badge and edit icon -->
                    <div class="flex items-center justify-between">
                        ${levelBadge}
                        <svg class="w-4 h-4 text-violet-400 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                        </svg>
                    </div>
                </div>
            </div>
        `;
        
        // Add click handler
        emailDiv.addEventListener('click', () => {
            this.openEmail(email, index);
        });
        
        return emailDiv;
    }

    /**
     * Get email snippet/preview text
     */
    getEmailSnippet(email) {
        // Try different content fields from backend
        const content = email.decrypted_content || 
                       email.original_content || 
                       email.body || 
                       email.content || 
                       email.text || 
                       email.snippet || 
                       '';
        
        if (!content) return 'No content';
        
        // Clean and truncate content
        const cleanContent = this.decodeUtf8String(content)
            .replace(/<[^>]*>/g, '') // Remove HTML tags
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim();
        
        return cleanContent.length > 60 ? cleanContent.substring(0, 60) + '...' : cleanContent;
    }

    /**
     * Format email content for better readability
     */
    formatEmailContent(content) {
        if (!content) return 'No content';
        
        // Decode UTF-8 strings and clean up
        let formattedContent = this.decodeUtf8String(content);
        
        // Handle HTML content
        if (formattedContent.includes('<') && formattedContent.includes('>')) {
            // Convert HTML to plain text but preserve line breaks
            formattedContent = formattedContent
                .replace(/<br\s*\/?>/gi, '\n')
                .replace(/<\/p>/gi, '\n\n')
                .replace(/<[^>]*>/g, '') // Remove all HTML tags
                .replace(/&nbsp;/g, ' ')
                .replace(/&amp;/g, '&')
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>')
                .replace(/&quot;/g, '"')
                .replace(/&#39;/g, "'");
        }
        
        // Normalize whitespace and line breaks
        formattedContent = formattedContent
            .replace(/\r\n/g, '\n')
            .replace(/\r/g, '\n')
            .replace(/\n{3,}/g, '\n\n') // Max 2 consecutive line breaks
            .replace(/[ \t]+/g, ' ') // Normalize spaces and tabs
            .trim();
        
        return this.escapeHtml(formattedContent);
    }

    /**
     * Get initials from name
     */
    getInitials(name) {
        if (!name) return '?';
        const parts = name.split(/[<@\s]+/);
        const firstPart = parts[0] || '?';
        return firstPart.charAt(0).toUpperCase();
    }

    /**
     * Get QuMail security level
     */
    getQuMailLevel(email) {
        if (email.security_level) {
            return `Level ${email.security_level}`;
        }
        
        // Try to extract from algorithm
        const algorithm = email.algorithm || '';
        if (algorithm.includes('OTP') || algorithm.includes('Quantum Secure')) {
            return 'Level 1: Quantum Secure';
        } else if (algorithm.includes('Quantum-aided AES')) {
            return 'Level 2: Quantum-aided AES';
        } else if (algorithm.includes('Hybrid PQC') || algorithm.includes('ML-KEM')) {
            return 'Level 3: Hybrid PQC';
        } else if (algorithm.includes('Classical') || algorithm.includes('No Quantum')) {
            return 'Level 4: Classical';
        }
        
        return 'QuMail Encrypted';
    }

    /**
     * Format time ago (like "2m", "15m", "1h")
     */
    formatTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffMinutes < 60) {
            return `${diffMinutes}m`;
        } else if (diffHours < 24) {
            return `${diffHours}h`;
        } else {
            return `${diffDays}d`;
        }
    }

    /**
     * Get avatar color based on sender name
     */
    getAvatarColor(name) {
        const colors = [
            'from-violet-500 to-purple-600',
            'from-blue-500 to-indigo-600', 
            'from-green-500 to-emerald-600',
            'from-red-500 to-pink-600',
            'from-yellow-500 to-orange-600',
            'from-cyan-500 to-teal-600'
        ];
        
        // Simple hash function to consistently assign colors
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    }

    /**
     * Get display name from email address
     */
    getDisplayName(from) {
        if (!from) return 'Unknown Sender';
        
        // Clean up the input first
        let cleanFrom = this.decodeUtf8String(from).trim();
        
        // Handle quoted names like "John Doe" <email@domain.com>
        const quotedNameMatch = cleanFrom.match(/^"([^"]+)"\s*<.*>$/);
        if (quotedNameMatch) {
            return quotedNameMatch[1].trim();
        }
        
        // Handle name <email> format, extract the name
        const nameMatch = cleanFrom.match(/^([^<]+)<.*>$/);
        if (nameMatch) {
            const name = nameMatch[1].trim();
            // Remove quotes if present
            return name.replace(/^["']|["']$/g, '').trim();
        }
        
        // If it's just an email, use the part before @
        const emailMatch = cleanFrom.match(/^([^@]+)@/);
        if (emailMatch) {
            const username = emailMatch[1];
            // Convert dots and underscores to spaces and capitalize
            return username.replace(/[._-]/g, ' ')
                          .replace(/\b\w/g, l => l.toUpperCase())
                          .trim();
        }
        
        // If it looks like a name already, return as is
        if (cleanFrom.includes(' ') && !cleanFrom.includes('@')) {
            return cleanFrom;
        }
        
        return cleanFrom;
    }

    /**
     * Open an email for reading
     */
    async openEmail(email, index) {
        console.log(`📖 Opening email: ${email.subject}`);
        console.log('📧 Full email data:', email); // Debug log to see actual data
        
        this.currentEmail = email;
        
        // Update reader content
        this.updateEmailReader(email);
        
        // Show reader
        this.showEmailReader();
    }

    /**
     * Update email reader with email content
     */
    updateEmailReader(email) {
        const subjectElement = document.getElementById('email-reader-subject');
        const contentElement = document.getElementById('email-reader-content');
        
        if (!subjectElement || !contentElement) return;
        
        // Update subject
        subjectElement.textContent = this.decodeUtf8String(email.subject || 'No Subject');
        
        // Build full email content
        let emailHtml = this.buildEmailHtml(email);
        
        // Update content
        contentElement.innerHTML = emailHtml;
    }

    /**
     * Build full email HTML
     */
    buildEmailHtml(email) {
        // Extract email data with proper field mapping from backend
        const from = email.sender || email.from || 'Unknown Sender';
        const to = email.recipient || email.to || email.recipients || 'Unknown Recipient';
        const date = email.received_at || email.date || email.timestamp;
        const formattedDate = date ? new Date(date).toLocaleString() : 'Unknown Date';
        const isQuMail = email.is_qumail || false;
        
        let content = '';
        
        // Email Headers
        content += `
            <div class="bg-violet-500/10 p-4 rounded-lg mb-6 border border-violet-500/20">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="text-violet-300 font-medium">From:</span>
                        <span class="text-white ml-2">${this.escapeHtml(from)}</span>
                    </div>
                    <div>
                        <span class="text-violet-300 font-medium">To:</span>
                        <span class="text-white ml-2">${this.escapeHtml(to)}</span>
                    </div>
                    <div>
                        <span class="text-violet-300 font-medium">Date:</span>
                        <span class="text-white ml-2">${formattedDate}</span>
                    </div>
                    <div>
                        <span class="text-violet-300 font-medium">Type:</span>
                        <span class="text-white ml-2">${isQuMail ? '🔐 QuMail Encrypted' : '📧 Regular Email'}</span>
                    </div>
                </div>
            </div>
        `;
        
        // Email Body
        content += '<div class="prose prose-invert max-w-none">';
        
        if (isQuMail) {
            // QuMail email handling
            if (email.decryption_successful === true) {
                content += `
                    <div class="bg-green-500/10 border border-green-500/30 p-4 rounded-lg mb-4">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="text-green-400">✅</span>
                            <span class="text-green-300 font-medium">Decryption Successful</span>
                        </div>
                        <div class="text-sm text-green-200">
                            Algorithm: ${email.algorithm || 'Unknown'}
                        </div>
                    </div>
                    <div class="text-white whitespace-pre-wrap">${this.formatEmailContent(email.decrypted_content || email.original_content || email.body || email.content || email.text || 'No content')}</div>
                `;
            } else if (email.decryption_successful === false) {
                content += `
                    <div class="bg-red-500/10 border border-red-500/30 p-4 rounded-lg mb-4">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="text-red-400">❌</span>
                            <span class="text-red-300 font-medium">Decryption Failed</span>
                        </div>
                        <div class="text-sm text-red-200">
                            ${email.decryption_error || 'Unknown error'}
                        </div>
                    </div>
                    <div class="bg-gray-800/50 p-4 rounded-lg">
                        <h4 class="text-violet-300 font-medium mb-2">Encrypted Content:</h4>
                        <pre class="text-gray-300 text-xs whitespace-pre-wrap font-mono">${this.escapeHtml(email.original_content || email.body || email.content || email.text || 'No content available')}</pre>
                    </div>
                `;
            } else {
                // Show encrypted content (fallback)
                content += `
                    <div class="bg-violet-500/10 border border-violet-500/30 p-4 rounded-lg mb-4">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="text-violet-400">🔐</span>
                            <span class="text-violet-300 font-medium">QuMail Encrypted</span>
                        </div>
                    </div>
                    <div class="bg-gray-800/50 p-4 rounded-lg">
                        <h4 class="text-violet-300 font-medium mb-2">Encrypted Content:</h4>
                        <pre class="text-gray-300 text-xs whitespace-pre-wrap font-mono">${this.escapeHtml(email.original_content || email.body || email.content || email.text || 'No content available')}</pre>
                    </div>
                `;
            }
        } else {
            // Regular email - use proper content field from backend
            const emailBody = email.original_content || email.body || email.content || email.text || email.snippet || 'No content available';
            content += `<div class="text-white whitespace-pre-wrap">${this.formatEmailContent(emailBody)}</div>`;
        }
        
        content += '</div>';
        
        return content;
    }

    /**
     * Update folder count in sidebar
     */
    updateFolderCount(folderName, count) {
        const countElement = document.getElementById(`${folderName}-count`);
        if (countElement) {
            countElement.textContent = count.toString();
            countElement.style.display = count > 0 ? 'block' : 'none';
        }
    }

    /**
     * Show credentials required message
     */
    showCredentialsRequired() {
        if (!this.emailList) return;
        
        this.emailList.innerHTML = `
            <div class="text-center py-8 text-violet-300">
                <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
                <p class="text-lg font-medium">Gmail Configuration Required</p>
                <p class="text-sm opacity-75 mb-4">Please configure your Gmail App Password to access emails</p>
                <button onclick="window.quMailProfileManager?.showCenterModal()" class="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg transition-colors">
                    Configure Gmail
                </button>
            </div>
        `;
    }

    /**
     * Display error message
     */
    displayError(message) {
        if (!this.emailList) return;
        
        this.emailList.innerHTML = `
            <div class="text-center py-8 text-red-300">
                <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-lg font-medium">Error Loading Emails</p>
                <p class="text-sm opacity-75">${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Decode UTF-8 encoded strings (like =?UTF-8?Q?...?=)
     */
    decodeUtf8String(str) {
        if (!str) return '';
        
        // Check if it's a UTF-8 encoded string
        if (str.includes('=?UTF-8?Q?') || str.includes('=?utf-8?q?')) {
            try {
                // Remove the encoding wrapper and decode
                let decoded = str.replace(/=\?UTF-8\?Q\?/gi, '').replace(/\?=$/g, '');
                // Replace =XX with actual characters
                decoded = decoded.replace(/=([0-9A-F]{2})/gi, (match, hex) => {
                    return String.fromCharCode(parseInt(hex, 16));
                });
                // Replace underscores with spaces
                decoded = decoded.replace(/_/g, ' ');
                return decoded;
            } catch (e) {
                console.warn('Failed to decode UTF-8 string:', str, e);
                return str;
            }
        }
        
        return str;
    }

    /**
     * Refresh current folder
     */
    async refresh() {
        if (this.isLoading) return;
        await this.loadFolder(this.currentFolder);
    }
}

// Initialize email manager when DOM is ready
let quMailEmailManager = null;

async function initializeEmailManager() {
    try {
        quMailEmailManager = new QuMailEmailManager();
        await quMailEmailManager.initialize();
        
        // Make it globally available
        window.quMailEmailManager = quMailEmailManager;
        
        console.log('🚀 QuMail Email Manager fully initialized');
    } catch (error) {
        console.error('❌ Failed to initialize Email Manager:', error);
        
        // Retry after 2 seconds
        setTimeout(initializeEmailManager, 2000);
    }
}

// Start initialization when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEmailManager);
} else {
    initializeEmailManager();
}

console.log('📧 QuMail Email Manager script loaded');
