import argparse
import filecmp
import logging
import os
import shutil
import time
from pathlib import Path


class Node:
    ''' Class represents a node in synchronization. '''
    def __init__(self, path, name=''):
        self.name = name
        self.root_path = path
        self.files_list = os.listdir(path)


class Synchronizer:
    ''' Class represents a synchronization object. '''

    def __init__(self, name=''):
        self.name = name
        self.node_list = []
        self.files_copied_total = 0
        self.folders_copied_total = 0
        self.files_deleted_total = 0
        self.folders_deleted_total = 0

    def add_node(self, node):
        self.node_list.append(node)

    def compare_nodes(self):
        ''' Compares the nodes in the node_list.'''

        for node in self.node_list:
            if self.node_list.index(node) < len(self.node_list) - 1:
                node2 = self.node_list[self.node_list.index(node) + 1]
                print('\n Comparing Node ' + str(
                    self.node_list.index(node)+1) + ' and Node ' + str(
                        self.node_list.index(node) + 2) + ':')
                self._compare_directories(node.root_path, node2.root_path)

    def _compare_directories(self, left, right):
        ''' Compares directories. In case with common directory,
            compare what is inside of the directory by recursively call.
            If some directories/files is only in replica - method deleted them.
        '''

        result = filecmp.dircmp(left, right)
        if result.common_dirs:
            for res in result.common_dirs:
                self._compare_directories(
                    os.path.join(left, res), os.path.join(right, res))
        if result.left_only:
            self._copy(result.left_only, left, right)
        if result.right_only:
            for res in result.right_only:
                p = Path(os.path.join(right, res))
                if p.is_dir():
                    shutil.rmtree(os.path.join(right, res))
                    self.folders_deleted_total = self.folders_deleted_total + 1
                    logging.info('Deleted directory \"' + os.path.basename(res)
                                 + '\" from \"' + os.path.join(right))
                else:
                    os.remove(os.path.join(right, res))
                    self.files_deleted_total = self.files_deleted_total + 1
                    logging.info('Deleted \"' + os.path.basename(res) +
                                 '\" from \"' + os.path.join(right))
        left_newer = []
        right_newer = []
        if result.diff_files:
            for res in result.diff_files:
                l_modified = os.stat(os.path.join(left, res)).st_mtime
                r_modified = os.stat(os.path.join(right, res)).st_mtime
                if l_modified > r_modified:
                    left_newer.append(res)
                else:
                    right_newer.append(res)
        self._copy(left_newer, left, right)
        self._copy(right_newer, right, left)

    def _copy(self, files_list, src, dest):

        ''' Copies a list of files from a source to a destination node.'''
        for f in files_list:
            srcpath = os.path.join(src, os.path.basename(f))
            if os.path.isdir(srcpath):
                shutil.copytree(srcpath, os.path.join(
                    dest, os.path.basename(f)))
                self.folders_copied_total = self.folders_copied_total + 1
                logging.info('Copied directory \"' + os.path.basename(srcpath)
                             + '\" from \"' + os.path.dirname(srcpath)
                             + '\" to \"' + dest + '\"')
            else:
                shutil.copy2(srcpath, dest)
                self.files_copied_total = self.files_copied_total + 1
                logging.info('Copied \"' + os.path.basename(srcpath) +
                             '\" from \"' + os.path.dirname(srcpath) +
                             '\" to \"' + dest + '\"')


def create_parser():
    ''' Reads and adds argument values from the command line.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('path_source')
    parser.add_argument('path_target')
    parser.add_argument('interval', type=int)
    parser.add_argument('path_log')
    return parser


if __name__ == "__main__":

    parser = create_parser()
    namespace = parser.parse_args()

    ''' Adds logging in file and console. '''

    file_log = logging.FileHandler(namespace.path_log)
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out),
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.INFO)

    my_sync = Synchronizer()
    node1 = Node(namespace.path_source, 'node1')
    node2 = Node(namespace.path_target, 'node2')
    my_sync.add_node(node1)
    my_sync.add_node(node2)

    ''' Adds periodic function call, prints number of copy and delete
        operations.
    '''

    while True:
        my_sync.files_copied_total = my_sync.folders_copied_total = 0
        my_sync.files_deleted_total = my_sync.folders_deleted_total = 0
        my_sync.compare_nodes()

        print('Total files copied ' + str(my_sync.files_copied_total))
        print('Total folders copied ' + str(my_sync.folders_copied_total))
        print('Total files deleted ' + str(my_sync.files_deleted_total))
        print('Total folders deleted ' + str(my_sync.folders_deleted_total))
        time.sleep(namespace.interval)
