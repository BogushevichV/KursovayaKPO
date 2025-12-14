API Reference
=============

Модули базы данных
------------------

.. toctree::
   :maxdepth: 2

   database_manager
   database_saver
   db_validation
   password_hasher

Пользовательская система
------------------------

.. toctree::
   :maxdepth: 2

   user_creator
   user_remover
   user_window

Административная система
------------------------

.. toctree::

   admin_creator
   admin_remover
   admin_window

Управление отчетами
-------------------

.. toctree::

   report_manager
   excel_importer
   grade_item_delegate

Основные классы
---------------

.. autosummary::
   :toctree: _autosummary
   :recursive:

   Main.Application
   DataBase.Database_Manager.DatabaseManager
   DataBase.Password_Hasher.PasswordHasher
   Report_Manager.ReportManager
   User.User_Creator.UserCreator
   Admin.Admin_Creator.AdminCreator
   Excel_Importer.ExcelImporter
   Grade_Item_Delegate.GradeItemDelegate