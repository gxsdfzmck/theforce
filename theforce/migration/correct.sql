-- 更新uniscore中的引用
update uniscore u, datamodel.university_name_mapping m
set u.uid = m.standard_id
where u.uid is null and u.uname=m.verbose_name;
update uniscore s, sdb.sdb_university u
set s.belong=u.belonging, s.is985=u.is_985, s.is211=u.is_211,
s.pid=u.province_id, s.type=u.university_type, s.urank=u.ranking
where s.uid=u.id;
update uniscore s, sdb.sdb_university_info i 
set s.city=i.city
where s.uid=i.uid;
update uniscore s, sdb.sdb_province p
set s.pname=p.name
where s.pid=p.id;
update uniscore s, sdb.sdb_xyh_ranking r, sdb.sdb_university u
set s.utyperank=r.utype_ranking
where u.name=r.university_name and u.id=s.uid;

-- 更新zhyscore中的引用
update zhyscore_7 u, datamodel.university_name_mapping m
set u.uid = m.standard_id
where u.uid is null and u.uname=m.verbose_name;
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
