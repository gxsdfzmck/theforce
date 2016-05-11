drop table if exists `zhyscore_7`;

CREATE TABLE `zhyscore_7` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `uname` varchar(50) DEFAULT NULL,
  `is985` tinyint(1) DEFAULT NULL,
  `is211` tinyint(1) DEFAULT NULL,
  `pid` int(11) DEFAULT NULL,
  `pname` varchar(50) DEFAULT NULL,
  `city` varchar(30) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `belong` varchar(20) DEFAULT NULL,
  `subject` varchar(10) DEFAULT NULL,
  `zhyid` int(11) DEFAULT NULL,
  `zhyname` varchar(50) DEFAULT NULL,
  `zhyrank` varchar(8) DEFAULT NULL,
  `enroll2016` int(11) DEFAULT NULL COMMENT '2016招生计划',
  `enroll2015` int(11) DEFAULT NULL COMMENT '2015招生计划',
  `enroll2014` int(11) DEFAULT NULL COMMENT '2014招生计划',
  `enroll2013` int(11) DEFAULT NULL COMMENT '2013招生计划',
  `arank2015` int(11) DEFAULT NULL COMMENT '2015最低排名',
  `arank2014` int(11) DEFAULT NULL COMMENT '2014录取最低排名',
  `arank2013` int(11) DEFAULT NULL COMMENT '2013录取最低排名',
  `ascore2015` int(11) DEFAULT NULL COMMENT '2015录取最低分',
  `ascore2014` int(11) DEFAULT NULL COMMENT '2014录取最低分',
  `ascore2013` int(11) DEFAULT NULL COMMENT '2013录取最低分',
  `abatch2015` varchar(10) DEFAULT NULL COMMENT '2015录取批次',
  `abatch2014` varchar(10) DEFAULT NULL COMMENT '2014年录取批次',
  `abatch2013` varchar(10) DEFAULT NULL COMMENT '2013年录取批次',
  `abatch2016` varchar(10) DEFAULT NULL,
  `urank` int(11) DEFAULT NULL COMMENT '总排名',
  `utyperank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*处理院校录取数据*/
insert into zhyscore_7(uname, subject, zhyname)
 select distinct university_name, subject_name, major_name
 from rd2016.m_score_7;

/*按年份处理录取数据*/
update zhyscore_7 u, rd2016.m_score_7 s
 set u.enroll2015=s.adm_number, u.ascore2015=s.adm_score, u.abatch2015=s.batching_name
 where s.year=2015 and u.subject=s.subject_name and u.uname=s.university_name and u.zhyname=s.major_name;

update zhyscore_7 u, rd2016.m_score_7 s
 set u.enroll2014=s.adm_number, u.ascore2014=s.adm_score, u.abatch2014=s.batching_name
 where s.year=2014 and u.subject=s.subject_name and u.uname=s.university_name and u.zhyname=s.major_name;

update zhyscore_7 u, rd2016.m_score_7 s
 set u.enroll2013=s.adm_number, u.ascore2013=s.adm_score, u.abatch2013=s.batching_name
 where s.year=2013 and u.subject=s.subject_name and u.uname=s.university_name and u.zhyname=s.major_name;

update zhyscore_7 u, dev_sdb.sdb_leveled_file_ranking2 r
 set u.arank2015=r.ranking
 where u.ascore2015 is not null and r.year=2015 and r.province_id=7
 and u.subject=r.subject_name and u.ascore2015>=r.score_min and u.ascore2015<=r.score_max;

update zhyscore_7 u, dev_sdb.sdb_leveled_file_ranking2 r
 set u.arank2014=r.ranking
 where u.ascore2014 is not null and r.year=2014 and r.province_id=7
 and u.subject=r.subject_name and u.ascore2014>=r.score_min and u.ascore2014<=r.score_max;

update zhyscore_7 u, dev_sdb.sdb_leveled_file_ranking2 r
 set u.arank2013=r.ranking
 where u.ascore2013 is not null and r.year=2013 and r.province_id=7
 and u.subject=r.subject_name and u.ascore2013>=r.score_min and u.ascore2013<=r.score_max;


/*处理学校相关信息数据*/
update zhyscore_7 s, sdb.sdb_university u
set s.uid=u.id
where s.uname = u.name;

update zhyscore_7 s, sdb.sdb_university u
 set s.belong=u.belonging, s.is985=u.is_985, s.is211=u.is_211,
 s.pid=u.province_id, s.type=u.university_type, s.urank=u.ranking
 where s.uid=u.id;
update zhyscore_7 s, sdb.sdb_university_info i 
 set s.city=i.city
 where s.uid=i.uid;
update zhyscore_7 s, sdb.sdb_province p
 set s.pname=p.name
 where s.pid=p.id;
update zhyscore_7 s, sdb.sdb_xyh_ranking r, sdb.sdb_university u
 set s.utyperank=r.utype_ranking
 where u.name=r.university_name and u.id=s.uid;

/* TODO 处理专业信息 */
update zhyscore_7 s, sdb.sdb_major m
  set s.zhyid=m.id
  where s.zhyname=m.`name`;

/*
update zhyscore_7 u, datamodel.university_name_mapping m
set u.uid = m.standard_id
where u.uid is null and u.uname=m.verbose_name;

update uniscore u, datamodel.university_name_mapping m
set u.uid = m.standard_id
where u.uid is null and u.uname=m.verbose_name;
*/
