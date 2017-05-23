#!/usr/bin/env python
# coding=utf-8

import sys, glob, os, re, ctypes


def handle(pathDir,time):
    o_fd = open(u'%s_数据.txt' %time, 'w')
    o_fd.write('ax ay az gx gy gz mx my mz'.replace(' ', ' ' * 3))

    flash_addr = 0xE8000
    for line in open(pathDir, 'r'):
        line = line.strip()
        if not len(line):
            continue

        sp = line.split(':')
        if len(sp) < 2:
            continue
        cur_addr = int(sp[0], base=16)
        if cur_addr != flash_addr:
            print '数据有丢失', line, hex(cur_addr), hex(flash_addr)
        # break
        flash_addr = cur_addr + 18

        if sp[1] == 'f' * 36:
            continue

        u16s = [0] * 9
        for i in range(9):
            u16s[i] = int(sp[1][i * 4:i * 4 + 4], base=16)
        if 0xdcba == u16s[0] and (0x4321 == u16s[1] or 0x9876 == u16s[1]):
            sec = (u16s[2] + (u16s[3] << 16)) % (24 * 60 * 60)
            minute = sec / 60
            hour = minute / 60
            o_fd.write('time %d:%02d:%02d\t' % (hour, minute % 60, sec % 60))
            x = ctypes.c_short(u16s[4]).value
            y = ctypes.c_short(u16s[6]).value
            z = ctypes.c_short(u16s[8]).value
            if 0x9876 == u16s[1]:
                # 开始游泳，记录地磁校准值
                o_fd.write('mag_center= %d %d %d\n\n' % (x, y, z))
            else:
                o_fd.write('strokes=%d\tlaps=%d\tstyle=%d\n' % (x, y, z))
        else:
            for i in range(9):
                o_fd.write('%d ' % ctypes.c_short(u16s[i]).value)
            o_fd.write('\n')

    o_fd.close()

def get_data(time):
    file = open(u"%s_数据.txt" %time, 'r')
    k = 0
    list1 = []
    time_list=[]
    list = file.readlines()
    for i in range(len(list)):
        if "mag_center" in list[i]:
            k += 1
            list1.append(i)
    list1.append(len(list) - 1)
    s = 0
    while k > 0:

        o_fd = open(u'./九轴数据/九轴数据%s_%s.txt' % (time,k), 'w')
        for i in range(len(list) - (list1[s]) - 1):
            o_fd.write(list[i + (list1[s])])
            if i + (list1[s]) + 1 == list1[s + 1]:
                break

        o_fd.close()
        s += 1
        k -= 1

def print_data():
    file = glob.glob(u"./九轴数据/九轴数据*.txt")
    for i in range(len(file)):
        print file[i]
        file1= open(file[i],"r")
        lines =file1.readlines()
        for j in range(len(lines)):

            line = lines[j].split()
            if "time" not in lines[j]:
                if abs(int(line[6]))>1500 or abs(int(line[7]))>1500 or abs(int(line[8]))>1500:
                    print file[i],lines[j]

def run():
    file = glob.glob("*.log")
    for i in range(len(file)):
        time = file[i].split("RTT_Terminal_")[1].split(".")[0]
        handle(file[i],time)
        get_data(time)

if __name__ == '__main__':
    run()
    print_data()
