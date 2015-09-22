@echo off

set p=%~dp0
set luas_path=%p%luas
set config_path=%p%..\..\client-refactory\Develop\Assets\Resources\Script\Config
set table_path=%p%..\Lua\Table

echo %p%
echo %luas_path%
echo %config_path%
echo %table_path%

cd %p%
python excel2lua\excel2lua.py

rd /s /q %table_path%
md %table_path%
xcopy /y /e /h %luas_path% %table_path%

rd /s /q %config_path%
md %config_path%
xcopy /y /e /h %luas_path% %config_path%