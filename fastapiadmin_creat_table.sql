


SET FOREIGN_KEY_CHECKS = 0;   -- 临时关闭外键约束检查

-- =============================================
-- 一、项目表
-- =============================================
DROP TABLE IF EXISTS `project`;
CREATE TABLE `project` (
  `name` varchar(255) NOT NULL COMMENT '项目名称',
  `code` varchar(64) DEFAULT NULL COMMENT '项目编码',
  `no` varchar(64) DEFAULT NULL COMMENT '项目编号',

  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `uuid` varchar(64) NOT NULL DEFAULT (UUID()) COMMENT 'UUID全局唯一标识',
  `status` varchar(8) NOT NULL DEFAULT '0' COMMENT '是否启用(0:启用 1:禁用)',
  `description` text NULL COMMENT '备注/描述',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_id` int NULL COMMENT '创建人ID',
  `updated_id` int NULL COMMENT '更新人ID',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`),
  UNIQUE KEY `uk_project_uuid` (`uuid`),
  CONSTRAINT `fk_project_created_id` FOREIGN KEY (`created_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_project_updated_id` FOREIGN KEY (`updated_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目信息表';



-- =============================================
-- 二、部件表（一个项目对应多个部件）
-- =============================================
DROP TABLE IF EXISTS `component`;
CREATE TABLE `component` (
  `project_id` int NOT NULL COMMENT '所属项目id',
  `name` varchar(255) NOT NULL COMMENT '部件名称',
  `code` varchar(64) DEFAULT NULL COMMENT '部件编码',
  `count` int DEFAULT NULL COMMENT '数量',
  `tmass` int DEFAULT NULL COMMENT '总重',

  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `uuid` varchar(64) NOT NULL DEFAULT (UUID()) COMMENT 'UUID全局唯一标识',
  `status` varchar(8) NOT NULL DEFAULT '0' COMMENT '是否启用(0:启用 1:禁用)',
  `description` text NULL COMMENT '备注/描述',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_id` int NULL COMMENT '创建人ID',
  `updated_id` int NULL COMMENT '更新人ID',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_component_uuid` (`uuid`),
  UNIQUE KEY `uk_component_project_id` (`project_id`, `name`),
  CONSTRAINT `fk_component_project_id` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_component_created_id` FOREIGN KEY (`created_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_component_updated_id` FOREIGN KEY (`updated_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部件信息表';



-- =============================================
-- 三、工艺表
-- =============================================
DROP TABLE IF EXISTS `craft`;
CREATE TABLE `craft` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '工艺ID',
  `parent_id` int DEFAULT NULL COMMENT '父工艺ID',
  `name` varchar(255) NOT NULL COMMENT '工艺名称',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`),
  KEY `ix_craft_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工艺表';

-- 插入主工艺
INSERT INTO craft (id, parent_id, name) VALUES 
(1, NULL, '下料'),
(2, NULL, '铆焊'),
(3, NULL, '机加'),
(4, NULL, '喷漆'),
(5, NULL, '装配'),
(6, 3, '车削'),
(7, 3, '铣削'),
(8, 3, '钻削'),
(9, 3, '镗削'),
(10, 3, '刨削'),
(11, 1, '板材'),
(12, 1, '型材'),
(13, 4, '打磨'),
(14, 4, '底漆'),
(15, 4, '面漆');

-- =============================================
-- 四、生产工单表
-- =============================================
DROP TABLE IF EXISTS `worder`;
CREATE TABLE `worder` (
  `no` varchar(32) NOT NULL COMMENT '单号',
  `component_id` int NOT NULL COMMENT '部件id',
  `craft_id` int NOT NULL COMMENT '工艺id',
  `man_hour` int NOT NULL DEFAULT 0 COMMENT '工时',  
  `plan_count` int NOT NULL DEFAULT 1 COMMENT '计划数量',
  `real_count` int DEFAULT 0 COMMENT '实际数量',
  `plan_end_time` datetime NOT NULL COMMENT '计划完工时间',
  `real_end_time` datetime DEFAULT NULL COMMENT '实际完工时间',
  `plan_user_id` int NOT NULL COMMENT '计划执行用户',
  `real_user_id` int NOT NULL COMMENT '实际执行用户',

  `id` int NOT NULL AUTO_INCREMENT COMMENT '工单ID',  
  `uuid` varchar(64) NOT NULL DEFAULT (UUID()) COMMENT 'UUID',
  `status` varchar(10) NOT NULL DEFAULT '0' COMMENT '状态 0=待生产 1=生产中 2=已完成 3=已取消 4=已暂停',
  `description` text NULL COMMENT '备注/描述',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_id` int NULL COMMENT '创建人ID',
  `updated_id` int NULL COMMENT '更新人ID',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_worder_uuid` (`uuid`),
  UNIQUE KEY `uk_worder_no` (`no`),
  KEY `ix_worder_component_id` (`component_id`),
  KEY `ix_worder_craft_id` (`craft_id`),
  KEY `ix_worder_status` (`status`),
  KEY `ix_worder_plan_end_time` (`plan_end_time`),
  KEY `ix_worder_real_end_time` (`real_end_time`),
  KEY `ix_worder_plan_user_id` (`plan_user_id`),
  KEY `ix_worder_real_user_id` (`real_user_id`),
  CONSTRAINT `fk_worder_component_id` FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_worder_craft_id` FOREIGN KEY (`craft_id`) REFERENCES `craft` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_worder_plan_user_id` FOREIGN KEY (`plan_user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_worder_real_user_id` FOREIGN KEY (`real_user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_worder_created_id` FOREIGN KEY (`created_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_worder_updated_id` FOREIGN KEY (`updated_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='生产工单';


SET FOREIGN_KEY_CHECKS = 1;   -- 重新开启外键约束检查