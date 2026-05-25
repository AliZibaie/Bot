CREATE TABLE IF NOT EXISTS users (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    platform      VARCHAR(20)  NOT NULL,
    platform_user_id BIGINT   NOT NULL,
    username      VARCHAR(255),
    created_at    DATETIME     NOT NULL DEFAULT NOW(),
    updated_at    DATETIME     NOT NULL DEFAULT NOW(),
    UNIQUE KEY uq_platform_user (platform, platform_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS search_logs (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id    INT UNSIGNED NOT NULL,
    platform   VARCHAR(20)  NOT NULL,
    service    VARCHAR(20)  NOT NULL,
    query      TEXT         NOT NULL,
    created_at DATETIME     NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS download_logs (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id    INT UNSIGNED NOT NULL,
    platform   VARCHAR(20)  NOT NULL,
    service    VARCHAR(20)  NOT NULL,
    url        TEXT         NOT NULL,
    quality    VARCHAR(20),
    created_at DATETIME     NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
