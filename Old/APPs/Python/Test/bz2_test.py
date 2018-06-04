#import zipfile
#a= open('package2_2.raw')
#azip = zipfile.ZipFile('bb.zip', 'w',zipfile.ZIP_DEFLATED)
#azip.writestr('package2_2', str)
#azip.write('1.txt')
#azip.close()

import tarfile
import bz2
archive = tarfile.open('a.tar.bz2','w:bz2')
archive.debug = 1
archive.add(r'package2_2.rf_raw')
archive.close()