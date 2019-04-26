-- phpMyAdmin SQL Dump
-- version phpStudy 2014
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2019 年 04 月 24 日 09:36
-- 服务器版本: 5.5.53
-- PHP 版本: 5.4.45

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `flerken`
--

-- --------------------------------------------------------

--
-- 表的结构 `results`
--

CREATE TABLE IF NOT EXISTS `results` (
  `rid` int(100) NOT NULL AUTO_INCREMENT,
  `cmd` text NOT NULL,
  `hash` varchar(500) NOT NULL,
  `obfuscated` varchar(20) NOT NULL,
  `likely_platform` varchar(20) NOT NULL,
  `selected_platform` varchar(20) NOT NULL,
  `reason` varchar(50) NOT NULL,
  `measure_time` varchar(50) NOT NULL,
  `submit_ip` varchar(100) NOT NULL,
  `submit_time` datetime NOT NULL,
  PRIMARY KEY (`rid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=31 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
