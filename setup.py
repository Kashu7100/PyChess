from setuptools import setup, find_packages

setup(name='PyChess',
      version='0.0.1',
      description='PyChess is a pure Python chess library with move generation and move validation as well as GUI',
      author='Kashu',
      author_email='echo_six0566@yahoo.co.jp',
      url='https://github.com/Kashu7100/PyChess',
      packages=find_packages(),
      entry_points="""
      [console_scripts]
      chess = pychess.gui:main
      """,
      include_package_data=True,)
