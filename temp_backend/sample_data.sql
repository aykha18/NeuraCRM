-- Truncate all tables (order matters for FKs)
TRUNCATE watcher, deal_tag, activities, messages, deals, leads, contacts, users, stages, channels, tags RESTART IDENTITY CASCADE;

-- Stages (Kanban columns)
INSERT INTO stages (id, name, "order", wip_limit) VALUES
  (1, 'New', 1, 10),
  (2, 'Contacted', 2, 10),
  (3, 'Proposal Sent', 3, 10),
  (4, 'Negotiation', 4, 10),
  (5, 'Won', 5, 10),
  (6, 'Lost', 6, 10);

-- Channels
INSERT INTO channels (id, name, is_group, created_at) VALUES
  (1, 'General', true, NOW() - INTERVAL '60 days'),
  (2, 'VIP Clients', true, NOW() - INTERVAL '55 days'),
  (3, 'Operations', true, NOW() - INTERVAL '50 days'),
  (4, 'AI Insights', true, NOW() - INTERVAL '45 days');

-- Users (15, Indian and Middle Eastern names)
INSERT INTO users (id, name, email, password_hash, avatar_url, role, created_at) VALUES
  (1, 'Ayaan Khan', 'ayaan.khan@neuracrm.com', 'hash1', NULL, 'admin', NOW() - INTERVAL '59 days'),
  (2, 'Fatima Al Mansoori', 'fatima.mansoori@neuracrm.com', 'hash2', NULL, 'manager', NOW() - INTERVAL '58 days'),
  (3, 'Rohan Mehra', 'rohan.mehra@neuracrm.com', 'hash3', NULL, 'agent', NOW() - INTERVAL '57 days'),
  (4, 'Sara Al Farsi', 'sara.alfarsi@neuracrm.com', 'hash4', NULL, 'agent', NOW() - INTERVAL '56 days'),
  (5, 'Imran Patel', 'imran.patel@neuracrm.com', 'hash5', NULL, 'agent', NOW() - INTERVAL '55 days'),
  (6, 'Layla Nasser', 'layla.nasser@neuracrm.com', 'hash6', NULL, 'agent', NOW() - INTERVAL '54 days'),
  (7, 'Omar Al Hashimi', 'omar.hashimi@neuracrm.com', 'hash7', NULL, 'agent', NOW() - INTERVAL '53 days'),
  (8, 'Priya Sharma', 'priya.sharma@neuracrm.com', 'hash8', NULL, 'agent', NOW() - INTERVAL '52 days'),
  (9, 'Yousef Al Suwaidi', 'yousef.suwaidi@neuracrm.com', 'hash9', NULL, 'agent', NOW() - INTERVAL '51 days'),
  (10, 'Sneha Reddy', 'sneha.reddy@neuracrm.com', 'hash10', NULL, 'agent', NOW() - INTERVAL '50 days'),
  (11, 'Hassan Jaber', 'hassan.jaber@neuracrm.com', 'hash11', NULL, 'agent', NOW() - INTERVAL '49 days'),
  (12, 'Aisha Siddiqui', 'aisha.siddiqui@neuracrm.com', 'hash12', NULL, 'agent', NOW() - INTERVAL '48 days'),
  (13, 'Zainab Al Mazrouei', 'zainab.mazrouei@neuracrm.com', 'hash13', NULL, 'agent', NOW() - INTERVAL '47 days'),
  (14, 'Vikram Singh', 'vikram.singh@neuracrm.com', 'hash14', NULL, 'agent', NOW() - INTERVAL '46 days'),
  (15, 'Mariam Al Shamsi', 'mariam.shamsi@neuracrm.com', 'hash15', NULL, 'agent', NOW() - INTERVAL '45 days');

-- (The rest of the script would continue with contacts, leads, deals, activities, messages, tags, deal_tag, watcher, using realistic and AI-flavored data, and ensuring all FKs are valid. For brevity, only the first part is shown here. The full script would be several hundred lines.) 