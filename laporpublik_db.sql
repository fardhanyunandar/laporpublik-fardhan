-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Waktu pembuatan: 17 Jul 2026 pada 13.44
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `laporpublik_db`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `admin_notifications`
--

CREATE TABLE `admin_notifications` (
  `id` int(11) NOT NULL,
  `type` enum('new_report','sos','user_register','report_update','system') DEFAULT 'new_report',
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `ref_id` int(11) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `admin_notifications`
--

INSERT INTO `admin_notifications` (`id`, `type`, `title`, `message`, `ref_id`, `is_read`, `created_at`) VALUES
(1, 'user_register', 'Pengguna Baru (Google): Fardhan Maulana Yunandar', 'Pengguna baru mendaftar via Google dengan email fardhanyundr@gmail.com.', 2, 1, '2026-07-16 08:20:40'),
(2, 'user_register', 'Pengguna Baru (Google): Boga Aing', 'Pengguna baru mendaftar via Google dengan email aingbobotoh3307@gmail.com.', 3, 1, '2026-07-16 08:44:20'),
(3, 'user_register', 'Pengguna Baru (Google): ridho firdaus lubis', 'Pengguna baru mendaftar via Google dengan email ridhofirdauslubis@gmail.com.', 4, 1, '2026-07-16 08:48:57'),
(4, 'user_register', 'Pengguna Baru (Google): Fardhan Maulana Yunandar', 'Pengguna baru mendaftar via Google dengan email fardhanmlnaa@gmail.com.', 5, 1, '2026-07-16 08:56:06');

-- --------------------------------------------------------

--
-- Struktur dari tabel `audit_logs`
--

CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(80) NOT NULL,
  `details` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(300) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `audit_logs`
--

INSERT INTO `audit_logs` (`id`, `user_id`, `action`, `details`, `ip_address`, `user_agent`, `created_at`) VALUES
(1, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:07:19'),
(2, 2, 'register_google', 'Email: fardhanyundr@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:20:40'),
(3, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:22:48'),
(4, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:25:31'),
(5, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:27:51'),
(6, 1, 'settings_update', 'Keys: [\'app_name\', \'sos_email\']', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:28:15'),
(7, 1, 'settings_update', 'Keys: [\'app_name\', \'sos_email\']', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:28:39'),
(8, 1, 'settings_update', 'Keys: [\'app_name\', \'sos_email\']', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:28:39'),
(9, 1, 'settings_update', 'Keys: [\'app_name\', \'sos_email\']', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:28:40'),
(10, 1, 'settings_update', 'Keys: [\'app_name\', \'sos_email\']', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:28:40'),
(11, 1, 'settings_update', 'Keys: [\'app_name\', \'sos_email\']', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:28:40'),
(12, 1, 'settings_update', 'Keys: [\'app_name\', \'sos_email\']', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:28:49'),
(13, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:31:50'),
(14, 1, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:33:10'),
(15, 3, 'register_google', 'Email: aingbobotoh3307@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:44:20'),
(16, 3, 'login_google', 'Email: aingbobotoh3307@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:44:20'),
(17, 3, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:45:11'),
(18, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:45:18'),
(19, 1, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', '2026-07-16 08:45:26'),
(20, 4, 'register_google', 'Email: ridhofirdauslubis@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:48:57'),
(21, 4, 'login_google', 'Email: ridhofirdauslubis@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:48:57'),
(22, 4, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:55:57'),
(23, 5, 'register_google', 'Email: fardhanmlnaa@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:56:06'),
(24, 5, 'login_google', 'Email: fardhanmlnaa@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:56:06'),
(25, 5, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:56:27'),
(26, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:56:30'),
(27, 5, 'account_deactivated', 'By admin 1', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:56:41'),
(28, 1, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:56:45'),
(29, 1, 'login_success', 'Provider: local', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:56:54'),
(30, 5, 'account_activated', 'By admin 1', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 08:57:00'),
(31, 1, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 09:01:22'),
(32, 2, 'login_google', 'Email: fardhanyundr@gmail.com', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 09:01:29'),
(33, 2, 'logout', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36', '2026-07-16 09:01:33');

-- --------------------------------------------------------

--
-- Struktur dari tabel `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `report_id` int(11) DEFAULT NULL,
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `type` enum('info','success','warning','error','sos') DEFAULT 'info',
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `oauth_accounts`
--

CREATE TABLE `oauth_accounts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `provider` varchar(30) NOT NULL,
  `provider_id` varchar(200) NOT NULL,
  `provider_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`provider_data`)),
  `access_token` text DEFAULT NULL,
  `refresh_token` text DEFAULT NULL,
  `token_expiry` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `oauth_accounts`
--

INSERT INTO `oauth_accounts` (`id`, `user_id`, `provider`, `provider_id`, `provider_data`, `access_token`, `refresh_token`, `token_expiry`, `created_at`, `updated_at`) VALUES
(1, 2, 'google', '100965050381161901821', '{\"iss\": \"https://accounts.google.com\", \"azp\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"aud\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"sub\": \"100965050381161901821\", \"email\": \"fardhanyundr@gmail.com\", \"email_verified\": true, \"nbf\": 1784164539, \"name\": \"Fardhan Maulana Yunandar\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocIkTc-evxWb7G5DBhjowPzhgE1yIQ6UfyhGo5iWL07DFJrgotSU9w=s96-c\", \"given_name\": \"Fardhan\", \"family_name\": \"Maulana Yunandar\", \"iat\": 1784164839, \"exp\": 1784168439, \"jti\": \"fe584a7ae89eccb24d9f3adea2a3f48530f4b4fe\"}', NULL, NULL, NULL, '2026-07-16 08:20:40', '2026-07-16 08:20:40'),
(2, 3, 'google', '104029283076306728121', '{\"iss\": \"https://accounts.google.com\", \"azp\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"aud\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"sub\": \"104029283076306728121\", \"email\": \"aingbobotoh3307@gmail.com\", \"email_verified\": true, \"nbf\": 1784165960, \"name\": \"Boga Aing\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocLpTei6l09qkGiuiWO3sFRLUg4ppGIT9mzE0EBCVlBQn_LOWg=s96-c\", \"given_name\": \"Boga\", \"family_name\": \"Aing\", \"iat\": 1784166260, \"exp\": 1784169860, \"jti\": \"8e8358acd7fef7dc53166f51131b21c7d97df209\"}', NULL, NULL, NULL, '2026-07-16 08:44:20', '2026-07-16 08:44:20'),
(3, 4, 'google', '111003095021424679887', '{\"iss\": \"https://accounts.google.com\", \"azp\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"aud\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"sub\": \"111003095021424679887\", \"email\": \"ridhofirdauslubis@gmail.com\", \"email_verified\": true, \"nbf\": 1784166236, \"name\": \"ridho firdaus lubis\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocJmo66cyNysUQyFK9VyOk_XbvO0ovVE0HRuU_Zj1S50jzCDK0Q=s96-c\", \"given_name\": \"ridho\", \"family_name\": \"firdaus lubis\", \"iat\": 1784166536, \"exp\": 1784170136, \"jti\": \"3ec3ec4e787468f8e3be0def0337972f1d8c021b\"}', NULL, NULL, NULL, '2026-07-16 08:48:57', '2026-07-16 08:48:57'),
(4, 5, 'google', '106057803002159607275', '{\"iss\": \"https://accounts.google.com\", \"azp\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"aud\": \"474791192289-jr7orb5vpgph06d7fk78o4lpnnbg5tkl.apps.googleusercontent.com\", \"sub\": \"106057803002159607275\", \"email\": \"fardhanmlnaa@gmail.com\", \"email_verified\": true, \"nbf\": 1784166665, \"name\": \"Fardhan Maulana Yunandar\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocK3SUwFU6l4lziSTS0q8hU-kSlaZ55vj_zlri13xRC8EG2-vg=s96-c\", \"given_name\": \"Fardhan\", \"family_name\": \"Maulana Yunandar\", \"iat\": 1784166965, \"exp\": 1784170565, \"jti\": \"f20a99a36be095262670b9d7c5ec4958f50dfb66\"}', NULL, NULL, NULL, '2026-07-16 08:56:06', '2026-07-16 08:56:06');

-- --------------------------------------------------------

--
-- Struktur dari tabel `password_resets`
--

CREATE TABLE `password_resets` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `token` varchar(64) NOT NULL,
  `expires_at` datetime NOT NULL,
  `is_used` tinyint(1) DEFAULT 0,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(300) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `ticket_id` varchar(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(300) NOT NULL,
  `category` varchar(80) NOT NULL,
  `subcategory` varchar(80) DEFAULT NULL,
  `description` text NOT NULL,
  `location_name` varchar(300) DEFAULT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `address_detail` text DEFAULT NULL,
  `district` varchar(120) DEFAULT NULL,
  `city` varchar(120) DEFAULT NULL,
  `province` varchar(120) DEFAULT NULL,
  `priority` enum('low','medium','high','critical') DEFAULT 'medium',
  `status` enum('pending','in_review','in_progress','resolved','rejected','closed') DEFAULT 'pending',
  `is_anonymous` tinyint(1) DEFAULT 0,
  `is_sos` tinyint(1) DEFAULT 0,
  `admin_notes` text DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `report_attachments`
--

CREATE TABLE `report_attachments` (
  `id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  `file_url` varchar(300) NOT NULL,
  `file_type` varchar(30) DEFAULT NULL,
  `file_size` bigint(20) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `report_timeline`
--

CREATE TABLE `report_timeline` (
  `id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  `actor_id` int(11) DEFAULT NULL,
  `actor_name` varchar(120) DEFAULT NULL,
  `action` varchar(80) NOT NULL,
  `old_status` varchar(40) DEFAULT NULL,
  `new_status` varchar(40) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `sos_events`
--

CREATE TABLE `sos_events` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `latitude` decimal(10,7) NOT NULL,
  `longitude` decimal(10,7) NOT NULL,
  `address` varchar(300) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `status` enum('active','resolved','false_alarm') DEFAULT 'active',
  `resolved_by` int(11) DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `system_settings`
--

CREATE TABLE `system_settings` (
  `id` int(11) NOT NULL,
  `key` varchar(80) NOT NULL,
  `value` text DEFAULT NULL,
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `system_settings`
--

INSERT INTO `system_settings` (`id`, `key`, `value`, `updated_at`) VALUES
(1, 'app_name', 'LaporPublik', '2026-07-16 08:28:49'),
(2, 'google_client_id', '', '2026-07-16 08:07:04'),
(3, 'google_maps_key', '', '2026-07-16 08:07:04'),
(4, 'max_upload_mb', '16', '2026-07-16 08:07:04'),
(5, 'sos_email', 'fardhanyundr@gmail.com', '2026-07-16 08:28:15'),
(6, 'max_login_attempts', '5', '2026-07-16 08:07:04'),
(7, 'lockout_duration_minutes', '15', '2026-07-16 08:07:04'),
(8, 'password_min_length', '8', '2026-07-16 08:07:04'),
(9, 'require_strong_password', '1', '2026-07-16 08:07:04');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `uid` varchar(36) NOT NULL DEFAULT uuid(),
  `full_name` varchar(120) NOT NULL,
  `email` varchar(160) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `nik` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `avatar_url` varchar(300) DEFAULT NULL,
  `password` varchar(256) DEFAULT NULL,
  `google_id` varchar(100) DEFAULT NULL,
  `auth_provider` enum('local','google') DEFAULT 'local',
  `role` enum('user','admin','superadmin') NOT NULL DEFAULT 'user',
  `is_active` tinyint(1) DEFAULT 1,
  `is_verified` tinyint(1) DEFAULT 0,
  `verify_token` varchar(64) DEFAULT NULL,
  `reset_token` varchar(64) DEFAULT NULL,
  `reset_expiry` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `login_count` int(11) DEFAULT 0,
  `failed_login_attempts` int(11) DEFAULT 0,
  `locked_until` datetime DEFAULT NULL,
  `password_changed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `uid`, `full_name`, `email`, `phone`, `nik`, `address`, `avatar_url`, `password`, `google_id`, `auth_provider`, `role`, `is_active`, `is_verified`, `verify_token`, `reset_token`, `reset_expiry`, `last_login`, `login_count`, `failed_login_attempts`, `locked_until`, `password_changed_at`, `created_at`, `updated_at`) VALUES
(1, '06420ca3-47e2-424f-a4cd-bba4ee4a93c0', 'Super Administrator', 'admin@lapor.id', '081234567890', NULL, NULL, NULL, 'scrypt:32768:8:1$Uot8Gl7ZJ0OSdHdm$82f3123d66747fe50afbd47f1675cf46185f520685961b4634a5d964a36c7d0d0f51054b69156d2575ed4efe2ceeb47e9adff6af15113ccb06974d801a900fd3', NULL, 'local', 'superadmin', 1, 1, NULL, NULL, NULL, '2026-07-16 08:56:54', 11, 0, NULL, NULL, '2026-07-16 08:07:04', '2026-07-16 08:56:54'),
(2, '04034d2a-4894-49ad-8ec1-03d3c48b5e5a', 'Fardhan Maulana Yunandar', 'fardhanyundr@gmail.com', NULL, NULL, NULL, 'https://lh3.googleusercontent.com/a/ACg8ocIkTc-evxWb7G5DBhjowPzhgE1yIQ6UfyhGo5iWL07DFJrgotSU9w=s96-c', NULL, '100965050381161901821', 'google', 'user', 1, 1, NULL, NULL, NULL, '2026-07-16 09:01:29', 5, 0, NULL, NULL, '2026-07-16 08:20:40', '2026-07-16 09:01:29'),
(3, 'cd3e0c1b-3fa2-4600-b822-fb731804d1a8', 'Boga Aing', 'aingbobotoh3307@gmail.com', NULL, NULL, NULL, 'https://lh3.googleusercontent.com/a/ACg8ocLpTei6l09qkGiuiWO3sFRLUg4ppGIT9mzE0EBCVlBQn_LOWg=s96-c', NULL, '104029283076306728121', 'google', 'user', 1, 1, NULL, NULL, NULL, '2026-07-16 08:44:20', 1, 0, NULL, NULL, '2026-07-16 08:44:20', '2026-07-16 08:44:20'),
(4, '570f0ee2-8d32-47e1-9dc5-3cedb05ffa08', 'ridho firdaus lubis', 'ridhofirdauslubis@gmail.com', NULL, NULL, NULL, 'https://lh3.googleusercontent.com/a/ACg8ocJmo66cyNysUQyFK9VyOk_XbvO0ovVE0HRuU_Zj1S50jzCDK0Q=s96-c', NULL, '111003095021424679887', 'google', 'user', 1, 1, NULL, NULL, NULL, '2026-07-16 08:48:57', 1, 0, NULL, NULL, '2026-07-16 08:48:57', '2026-07-16 08:48:57'),
(5, 'df785b97-af42-4445-9766-239757d3aadd', 'Fardhan Maulana Yunandar', 'fardhanmlnaa@gmail.com', NULL, NULL, NULL, 'https://lh3.googleusercontent.com/a/ACg8ocK3SUwFU6l4lziSTS0q8hU-kSlaZ55vj_zlri13xRC8EG2-vg=s96-c', NULL, '106057803002159607275', 'google', 'user', 1, 1, NULL, NULL, NULL, '2026-07-16 08:56:06', 1, 0, NULL, NULL, '2026-07-16 08:56:06', '2026-07-16 08:57:00');

-- --------------------------------------------------------

--
-- Struktur dari tabel `user_sessions`
--

CREATE TABLE `user_sessions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `session_id` varchar(100) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(300) DEFAULT NULL,
  `last_active` datetime DEFAULT current_timestamp(),
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `admin_notifications`
--
ALTER TABLE `admin_notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_read` (`is_read`),
  ADD KEY `idx_type` (`type`),
  ADD KEY `idx_created` (`created_at`);

--
-- Indeks untuk tabel `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user` (`user_id`),
  ADD KEY `idx_action` (`action`),
  ADD KEY `idx_created` (`created_at`),
  ADD KEY `idx_ip` (`ip_address`);

--
-- Indeks untuk tabel `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `report_id` (`report_id`),
  ADD KEY `idx_user_read` (`user_id`,`is_read`),
  ADD KEY `idx_created` (`created_at`);

--
-- Indeks untuk tabel `oauth_accounts`
--
ALTER TABLE `oauth_accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_provider_user` (`provider`,`user_id`),
  ADD UNIQUE KEY `uk_provider_id` (`provider`,`provider_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indeks untuk tabel `password_resets`
--
ALTER TABLE `password_resets`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `idx_token` (`token`),
  ADD KEY `idx_expires` (`expires_at`);

--
-- Indeks untuk tabel `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ticket_id` (`ticket_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_category` (`category`),
  ADD KEY `idx_priority` (`priority`),
  ADD KEY `idx_created` (`created_at`),
  ADD KEY `idx_user` (`user_id`),
  ADD KEY `idx_location` (`latitude`,`longitude`);

--
-- Indeks untuk tabel `report_attachments`
--
ALTER TABLE `report_attachments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_report` (`report_id`);

--
-- Indeks untuk tabel `report_timeline`
--
ALTER TABLE `report_timeline`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_report` (`report_id`),
  ADD KEY `idx_created` (`created_at`);

--
-- Indeks untuk tabel `sos_events`
--
ALTER TABLE `sos_events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_created` (`created_at`);

--
-- Indeks untuk tabel `system_settings`
--
ALTER TABLE `system_settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `key` (`key`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uid` (`uid`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `google_id` (`google_id`),
  ADD KEY `idx_email` (`email`),
  ADD KEY `idx_google_id` (`google_id`),
  ADD KEY `idx_role` (`role`),
  ADD KEY `idx_active` (`is_active`);

--
-- Indeks untuk tabel `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `session_id` (`session_id`),
  ADD KEY `idx_user` (`user_id`),
  ADD KEY `idx_session` (`session_id`),
  ADD KEY `idx_last_active` (`last_active`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `admin_notifications`
--
ALTER TABLE `admin_notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT untuk tabel `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `oauth_accounts`
--
ALTER TABLE `oauth_accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `password_resets`
--
ALTER TABLE `password_resets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `report_attachments`
--
ALTER TABLE `report_attachments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `report_timeline`
--
ALTER TABLE `report_timeline`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `sos_events`
--
ALTER TABLE `sos_events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `system_settings`
--
ALTER TABLE `system_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=208;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT untuk tabel `user_sessions`
--
ALTER TABLE `user_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE SET NULL;

--
-- Ketidakleluasaan untuk tabel `oauth_accounts`
--
ALTER TABLE `oauth_accounts`
  ADD CONSTRAINT `oauth_accounts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `password_resets`
--
ALTER TABLE `password_resets`
  ADD CONSTRAINT `password_resets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `report_attachments`
--
ALTER TABLE `report_attachments`
  ADD CONSTRAINT `report_attachments_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `report_timeline`
--
ALTER TABLE `report_timeline`
  ADD CONSTRAINT `report_timeline_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `sos_events`
--
ALTER TABLE `sos_events`
  ADD CONSTRAINT `sos_events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
