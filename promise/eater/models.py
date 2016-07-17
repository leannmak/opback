# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: July 12, 2016
#
# This is the model module of eater package.

from .. import db
from sqlalchemy.ext.declarative import declared_attr
import re


# default database bound
my_default_database = None


class MyModel(db.Model):
    """
        Eater Super Model.
    """
    __abstract__ = True

    # tablename
    @declared_attr
    def __tablename__(cls):
        pattern = re.compile(r'([A-Z]+[a-z]+|^[A-Z]+[^A-Z]*$)')
        words = pattern.findall(cls.__name__)
        tname = ''
        if len(words) > 1:
            for w in words[:-1]:
                tname += '%s_' % w
        tname += words[-1]
        return tname.lower()

    # uuid
    id = db.Column(db.String(64), primary_key=True)


"""
many-to-many relationships between OperatingSystem and OSUser
"""
user2os = db.Table(
    'user2os',
    db.Column('os_id', db.String(64), db.ForeignKey('operating_system.id')),
    db.Column('user_id', db.String(64), db.ForeignKey('osuser.id')),
    info={'bind_key': my_default_database}
)


"""
many-to-many relationships between ITEquipment and OSUser
"""
osuser2it = db.Table(
    'osuser2it',
    db.Column('it_id', db.String(64), db.ForeignKey('itequipment.id')),
    db.Column('osuser_id', db.String(64), db.ForeignKey('osuser.id')),
    info={'bind_key': my_default_database}
)


class IP(MyModel):
    """
        IP Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('if_id', 'id', name='_if_ip_uc'),
        db.UniqueConstraint('it_id', 'id', name='_it_ip_uc'),)

    # IP address
    ip_addr = db.Column(db.String(64), unique=True)
    # IP mask
    ip_mask = db.Column(db.String(64))
    # IP category (vm/pm/network/security/storage/vip/unused)
    ip_category = db.Column(db.String(64), nullable=False)
    # interface which IP belongs to
    if_id = db.Column(db.String(32), db.ForeignKey('interface.id'))
    # IT equipment which IP belongs to
    it_id = db.Column(db.String(64), db.ForeignKey('itequipment.id'))

    # constructor
    def __init__(self, id, ip_addr, ip_mask,
                 if_id, it_id, ip_category='unused'):
        self.id = id
        self.ip_addr = ip_addr
        self.ip_mask = ip_mask
        self.ip_category = ip_category
        self.if_id = if_id
        self.it_id = it_id

    def __repr__(self):
        return '<IP %r>' % self.id

    # get a interface
    def getInterface(self):
        return self.inf

    # get a list of related IT equipments
    def getITEquipment(self):
        return self.it


class Interface(MyModel):
    """
        Interface Model.
    """
    __bind_key__ = my_default_database

    # interface name
    name = db.Column(db.String(64), nullable=False)
    # IP
    ip = db.relationship('IP', backref='inf', lazy='dynamic')

    # constructor
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<Interface %r>' % self.id


class OperatingSystem(MyModel):
    """
        Operating System Model.
    """
    __bind_key__ = my_default_database

    # OS name
    name = db.Column(db.String(64), nullable=False)
    # OS version
    version = db.Column(db.String(64), nullable=False)
    # IT equipment
    it = db.relationship(
        'ITEquipment', backref='os', lazy='dynamic')
    # OS user
    user = db.relationship(
        'OSUser', secondary='user2os', backref='os', lazy='dynamic')

    # constructor
    def __init__(self, id, name, version):
        print 'i\'m here.'
        self.id = id
        self.name = name
        self.version = version

    def __repr__(self):
        return '<OperatingSystem %r>' % self.id


class OSUser(MyModel):
    """
        Operating System User Model.
        Set 'enable_typechecks=False' to enable subtype polymorphism.
    """
    # __tablename__ = 'osuser'
    __bind_key__ = my_default_database

    # OS user name
    name = db.Column(db.String(64), nullable=False)
    # OS user password
    password = db.Column(db.String(64))
    # OS user privilege
    privilege = db.Column(db.String(64))
    # IT equipment
    it = db.relationship(
        'ITEquipment', secondary='osuser2it',
        enable_typechecks=False, lazy='dynamic')

    # constructor
    def __init__(self, id, name, password, privilege):
        self.id = id
        self.name = name
        self.password = password
        self.privilege = privilege

    # for print
    def __repr__(self):
        return '<OSUser %r>' % self.id

    # get a list of related operating systems
    def getOS(self):
        return self.os


class Rack(MyModel):
    """
        Rack Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('it_id', 'id', name='_it_rack_uc'),)

    # rack label
    label = db.Column(db.String(64), nullable=False)
    # IT equipment which is installed in the rack
    it_id = db.Column(db.String(64), db.ForeignKey('itequipment.id'))

    # constructor
    def __init__(self, id, label, it_id):
        self.id = id
        self.label = label
        self.it_id = it_id

    def __repr__(self):
        return '<Rack %r>' % self.id


class ITEquipment(MyModel):
    """
        IT Equipment Model.
        Superclass of Computer, Network, Storage and Security.
        Set 'enable_typechecks=False' to enable subtype polymorphism.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('os_id', 'name', name='_os_it_uc'),)

    # IT equipment label
    label = db.Column(db.String(64))
    # IT equipment host name
    name = db.Column(db.String(64), nullable=False)
    # IT equipment setup time
    setup_time = db.Column(db.String(64))
    # operating system
    os_id = db.Column(db.String(32), db.ForeignKey('operating_system.id'))
    # OS user
    osuser = db.relationship(
        'OSUser', secondary='osuser2it',
        enable_typechecks=False, lazy='dynamic')
    # IT equipment IP
    ip = db.relationship(
        'IP', enable_typechecks=False, backref='it', lazy='dynamic')
    # IT equipment location
    rack = db.relationship(
        'Rack', enable_typechecks=False, backref='it', lazy='dynamic')

    # constructor
    def __init__(self, id, label, name, setup_time, os_id):
        self.id = id
        self.label = label
        self.name = name
        self.setup_time
        self.os_id = os_id

    def __repr__(self):
        return '<ITEquipment %r>' % self.id


class Computer(ITEquipment):
    """
        Computer Model.
        Child of ITEquipment.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('spec_id', 'id', name='_spec_com_uc'),)

    # use super class ITEquipment uuid as Computer uuid
    id = db.Column(
        db.String(64), db.ForeignKey('itequipment.id'),
        primary_key=True)
    # iscsi name
    iqn_id = db.Column(db.String(256))
    # business group id
    group_id = db.Column(db.String(64))
    # computer specification
    spec_id = db.Column(
        db.String(64), db.ForeignKey('computer_specification.id'))

    # constructor
    def __init__(self, id, iqn_id, group_id, spec_id,
                 label, name, setup_time, os_id):
        self.id = id
        self.iqn_id = iqn_id
        self.group_id = group_id
        self.spec_id = spec_id
        super(Computer, self).__init__(id, label, name, setup_time, os_id)

    def __repr__(self):
        return '<Computer %r>' % self.id


class ComputerSpecification(MyModel):
    """
        Computer Specification Model.
    """
    __bind_key__ = my_default_database

    # CPU main frequency
    cpu_fre = db.Column(db.String(64))
    # CPU number
    cpu_num = db.Column(db.Integer)
    # memory
    memory = db.Column(db.String(64))
    # hard disk size
    disk = db.Column(db.String(64))
    # IT equipment IP
    computer = db.relationship(
        'Computer', backref='spec', lazy='dynamic')

    # constructor
    def __init__(self, id, cpu_fre, cpu_num, memory, disk):
        self.id = id
        self.cpu_fre = cpu_fre
        self.cpu_num = cpu_num
        self.memory = memory
        self.disk = disk

    def __repr__(self):
        return '<ComputerSpecification %r>' % self.id


class PhysicalMachine(Computer):
    """
        Physical Machine Model.
        Child of Computer.
    """
    __bind_key__ = my_default_database

    # use super class Computer uuid as PysicalMachine uuid
    id = db.Column(
        db.String(64), db.ForeignKey('computer.id'),
        primary_key=True)
    # related virtual machines
    vm = db.relationship(
        'VirtualMachine',
        backref='pm',
        foreign_keys='VirtualMachine.pm_id',
        lazy='dynamic')

    # constructor
    def __init__(self, id, iqn_id, group_id, spec_id, label,
                 name, setup_time, os_id):
        self.id = id
        super(PhysicalMachine, self).__init__(
            id, iqn_id, group_id, spec_id, label, name, setup_time, os_id)

    def __repr__(self):
        return '<PhysicalMachine %r>' % self.id


class VirtualMachine(Computer):
    """
        Virtual Machine Model.
        Child of Computer.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('pm_id', 'vm_pid', name='_pm_vm_uc'),)

    # use super class Computer uuid as VirtualMachine uuid
    id = db.Column(
        db.String(64), db.ForeignKey('computer.id'),
        primary_key=True)
    # related pm
    pm_id = db.Column(
        db.String(64), db.ForeignKey('physical_machine.id'), nullable=False)
    # vm pid
    vm_pid = db.Column(db.String(64), nullable=False)

    # constructor
    def __init__(self, id, pm_id, vm_pid, iqn_id, group_id,
                 spec_id, label, name, setup_time, os_id):
        self.id = id
        self.pm_id = pm_id
        self.vm_pid = vm_pid
        super(VirtualMachine, self).__init__(
            id, iqn_id, group_id, spec_id, label, name, setup_time, os_id)

    def __repr__(self):
        return '<VirtualMachine %r>' % self.id

    # get the related pm
    def getPhysicalMachine(self):
        return self.pm