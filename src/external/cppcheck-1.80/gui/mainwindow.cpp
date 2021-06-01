/*
 * Cppcheck - A tool for static C/C++ code analysis
 * Copyright (C) 2007-2016 Cppcheck team.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <QApplication>
#include <QDebug>
#include <QMessageBox>
#include <QFileInfo>
#include <QDir>
#include <QDesktopServices>
#include <QUrl>
#include <QAction>
#include <QActionGroup>
#include <QFile>
#include <QInputDialog>
#include "mainwindow.h"
#include "cppcheck.h"
#include "applicationlist.h"
#include "aboutdialog.h"
#include "common.h"
#include "threadhandler.h"
#include "fileviewdialog.h"
#include "projectfile.h"
#include "project.h"
#include "report.h"
#include "scratchpad.h"
#include "statsdialog.h"
#include "settingsdialog.h"
#include "threadresult.h"
#include "translationhandler.h"
#include "logview.h"
#include "filelist.h"
#include "showtypes.h"
#include "librarydialog.h"

static const QString OnlineHelpURL("http://cppcheck.net/manual.html");
static const QString compile_commands_json("compile_commands.json");

MainWindow::MainWindow(TranslationHandler* th, QSettings* settings) :
    mSettings(settings),
    mApplications(new ApplicationList(this)),
    mTranslation(th),
    mLogView(NULL),
    mScratchPad(NULL),
    mProject(NULL),
    mPlatformActions(new QActionGroup(this)),
    mCStandardActions(new QActionGroup(this)),
    mCppStandardActions(new QActionGroup(this)),
    mSelectLanguageActions(new QActionGroup(this)),
    mExiting(false),
    mIsLogfileLoaded(false)
{
    mUI.setupUi(this);
    mThread = new ThreadHandler(this);
    mUI.mResults->initialize(mSettings, mApplications, mThread);

    // Filter timer to delay filtering results slightly while typing
    mFilterTimer = new QTimer(this);
    mFilterTimer->setInterval(500);
    mFilterTimer->setSingleShot(true);
    connect(mFilterTimer, SIGNAL(timeout()), this, SLOT(filterResults()));

    // "Filter" toolbar
    mLineEditFilter = new QLineEdit(mUI.mToolBarFilter);
    mLineEditFilter->setPlaceholderText(tr("Quick Filter:"));
    mUI.mToolBarFilter->addWidget(mLineEditFilter);
    connect(mLineEditFilter, SIGNAL(textChanged(const QString&)), mFilterTimer, SLOT(start()));
    connect(mLineEditFilter, SIGNAL(returnPressed()), this, SLOT(filterResults()));

    connect(mUI.mActionPrint, SIGNAL(triggered()), mUI.mResults, SLOT(print()));
    connect(mUI.mActionPrintPreview, SIGNAL(triggered()), mUI.mResults, SLOT(printPreview()));
    connect(mUI.mActionQuit, SIGNAL(triggered()), this, SLOT(close()));
    connect(mUI.mActionCheckFiles, SIGNAL(triggered()), this, SLOT(checkFiles()));
    connect(mUI.mActionCheckDirectory, SIGNAL(triggered()), this, SLOT(checkDirectory()));
    connect(mUI.mActionSettings, SIGNAL(triggered()), this, SLOT(programSettings()));
    connect(mUI.mActionClearResults, SIGNAL(triggered()), this, SLOT(clearResults()));
    connect(mUI.mActionOpenXML, SIGNAL(triggered()), this, SLOT(openResults()));

    connect(mUI.mActionShowStyle, SIGNAL(toggled(bool)), this, SLOT(showStyle(bool)));
    connect(mUI.mActionShowErrors, SIGNAL(toggled(bool)), this, SLOT(showErrors(bool)));
    connect(mUI.mActionShowWarnings, SIGNAL(toggled(bool)), this, SLOT(showWarnings(bool)));
    connect(mUI.mActionShowPortability, SIGNAL(toggled(bool)), this, SLOT(showPortability(bool)));
    connect(mUI.mActionShowPerformance, SIGNAL(toggled(bool)), this, SLOT(showPerformance(bool)));
    connect(mUI.mActionShowInformation, SIGNAL(toggled(bool)), this, SLOT(showInformation(bool)));
    connect(mUI.mActionCheckAll, SIGNAL(triggered()), this, SLOT(checkAll()));
    connect(mUI.mActionUncheckAll, SIGNAL(triggered()), this, SLOT(uncheckAll()));
    connect(mUI.mActionCollapseAll, SIGNAL(triggered()), mUI.mResults, SLOT(collapseAllResults()));
    connect(mUI.mActionExpandAll, SIGNAL(triggered()), mUI.mResults, SLOT(expandAllResults()));
    connect(mUI.mActionShowHidden, SIGNAL(triggered()), mUI.mResults, SLOT(showHiddenResults()));
    connect(mUI.mActionViewLog, SIGNAL(triggered()), this, SLOT(showLogView()));
    connect(mUI.mActionViewStats, SIGNAL(triggered()), this, SLOT(showStatistics()));
    connect(mUI.mActionLibraryEditor, SIGNAL(triggered()), this, SLOT(showLibraryEditor()));

    connect(mUI.mActionRecheckModified, SIGNAL(triggered()), this, SLOT(reCheckModified()));
    connect(mUI.mActionRecheckAll, SIGNAL(triggered()), this, SLOT(reCheckAll()));

    connect(mUI.mActionStop, SIGNAL(triggered()), this, SLOT(stopChecking()));
    connect(mUI.mActionSave, SIGNAL(triggered()), this, SLOT(save()));

    // About menu
    connect(mUI.mActionAbout, SIGNAL(triggered()), this, SLOT(about()));
    connect(mUI.mActionLicense, SIGNAL(triggered()), this, SLOT(showLicense()));

    // View > Toolbar menu
    connect(mUI.mActionToolBarMain, SIGNAL(toggled(bool)), this, SLOT(toggleMainToolBar()));
    connect(mUI.mActionToolBarView, SIGNAL(toggled(bool)), this, SLOT(toggleViewToolBar()));
    connect(mUI.mActionToolBarFilter, SIGNAL(toggled(bool)), this, SLOT(toggleFilterToolBar()));

    connect(mUI.mActionAuthors, SIGNAL(triggered()), this, SLOT(showAuthors()));
    connect(mThread, SIGNAL(done()), this, SLOT(checkDone()));
    connect(mUI.mResults, SIGNAL(gotResults()), this, SLOT(resultsAdded()));
    connect(mUI.mResults, SIGNAL(resultsHidden(bool)), mUI.mActionShowHidden, SLOT(setEnabled(bool)));
    connect(mUI.mResults, SIGNAL(checkSelected(QStringList)), this, SLOT(performSelectedFilesCheck(QStringList)));
    connect(mUI.mMenuView, SIGNAL(aboutToShow()), this, SLOT(aboutToShowViewMenu()));

    // File menu
    connect(mUI.mActionNewProjectFile, SIGNAL(triggered()), this, SLOT(newProjectFile()));
    connect(mUI.mActionOpenProjectFile, SIGNAL(triggered()), this, SLOT(openProjectFile()));
    connect(mUI.mActionShowScratchpad, SIGNAL(triggered()), this, SLOT(showScratchpad()));
    connect(mUI.mActionCloseProjectFile, SIGNAL(triggered()), this, SLOT(closeProjectFile()));
    connect(mUI.mActionEditProjectFile, SIGNAL(triggered()), this, SLOT(editProjectFile()));

    connect(mUI.mActionHelpContents, SIGNAL(triggered()), this, SLOT(openHelpContents()));

    loadSettings();

    mThread->initialize(mUI.mResults);
    formatAndSetTitle();

    enableCheckButtons(true);

    mUI.mActionPrint->setShortcut(QKeySequence::Print);
    mUI.mActionPrint->setEnabled(false);
    mUI.mActionPrintPreview->setEnabled(false);
    mUI.mActionClearResults->setEnabled(false);
    mUI.mActionSave->setEnabled(false);
    mUI.mActionRecheckModified->setEnabled(false);
    mUI.mActionRecheckAll->setEnabled(false);
    enableProjectOpenActions(true);
    enableProjectActions(false);

    // Must setup MRU menu before CLI param handling as it can load a
    // project file and update MRU menu.
    for (int i = 0; i < MaxRecentProjects; ++i) {
        mRecentProjectActs[i] = new QAction(this);
        mRecentProjectActs[i]->setVisible(false);
        connect(mRecentProjectActs[i], SIGNAL(triggered()),
                this, SLOT(openRecentProject()));
    }
    mRecentProjectActs[MaxRecentProjects] = NULL; // The separator
    mUI.mActionProjectMRU->setVisible(false);
    updateMRUMenuItems();

    QStringList args = QCoreApplication::arguments();
    //Remove the application itself
    args.removeFirst();
    if (!args.isEmpty()) {
        handleCLIParams(args);
    }

    for (int i = 0; i < mPlatforms.getCount(); i++) {
        Platform plat = mPlatforms.mPlatforms[i];
        QAction *act = new QAction(this);
        plat.mActMainWindow = act;
        mPlatforms.mPlatforms[i] = plat;
        act->setText(plat.mTitle);
        act->setData(plat.mType);
        act->setCheckable(true);
        act->setActionGroup(mPlatformActions);
        mUI.mMenuCheck->insertAction(mUI.mActionPlatforms, act);
        connect(act, SIGNAL(triggered()), this, SLOT(selectPlatform()));
    }

    mUI.mActionC89->setActionGroup(mCStandardActions);
    mUI.mActionC99->setActionGroup(mCStandardActions);
    mUI.mActionC11->setActionGroup(mCStandardActions);

    mUI.mActionCpp03->setActionGroup(mCppStandardActions);
    mUI.mActionCpp11->setActionGroup(mCppStandardActions);

    mUI.mActionEnforceC->setActionGroup(mSelectLanguageActions);
    mUI.mActionEnforceCpp->setActionGroup(mSelectLanguageActions);
    mUI.mActionAutoDetectLanguage->setActionGroup(mSelectLanguageActions);

    // For Windows platforms default to Win32 checked platform.
    // For other platforms default to unspecified/default which means the
    // platform Cppcheck GUI was compiled on.
#if defined(_WIN32)
    const Settings::PlatformType defaultPlat = Settings::Win32W;
#else
    const Settings::PlatformType defaultPlat = Settings::Unspecified;
#endif
    Platform &plat = mPlatforms.get((Settings::PlatformType)mSettings->value(SETTINGS_CHECKED_PLATFORM, defaultPlat).toInt());
    plat.mActMainWindow->setChecked(true);
}

MainWindow::~MainWindow()
{
    delete mLogView;
    delete mProject;
    delete mScratchPad;
}

void MainWindow::handleCLIParams(const QStringList &params)
{
    int index;
    if (params.contains("-p")) {
        index = params.indexOf("-p");
        if ((index + 1) < params.length())
            loadProjectFile(params[index + 1]);
    } else if (params.contains("-l")) {
        QString logFile;
        index = params.indexOf("-l");
        if ((index + 1) < params.length())
            logFile = params[index + 1];

        if (params.contains("-d")) {
            QString checkedDir;
            index = params.indexOf("-d");
            if ((index + 1) < params.length())
                checkedDir = params[index + 1];

            loadResults(logFile, checkedDir);
        } else {
            loadResults(logFile);
        }
    } else if ((index = params.indexOf(QRegExp(".*\\.cppcheck$", Qt::CaseInsensitive), 0)) >= 0 && index < params.length() && QFile(params[index]).exists()) {
        loadProjectFile(params[index]);
    } else if ((index = params.indexOf(QRegExp(".*\\.xml$", Qt::CaseInsensitive), 0)) >= 0 && index < params.length() && QFile(params[index]).exists()) {
        loadResults(params[index],QDir::currentPath());
    } else
        doCheckFiles(params);
}

void MainWindow::loadSettings()
{
    // Window/dialog sizes
    if (mSettings->value(SETTINGS_WINDOW_MAXIMIZED, false).toBool()) {
        showMaximized();
    } else {
        resize(mSettings->value(SETTINGS_WINDOW_WIDTH, 800).toInt(),
               mSettings->value(SETTINGS_WINDOW_HEIGHT, 600).toInt());
    }

    ShowTypes *types = mUI.mResults->getShowTypes();
    mUI.mActionShowStyle->setChecked(types->isShown(ShowTypes::ShowStyle));
    mUI.mActionShowErrors->setChecked(types->isShown(ShowTypes::ShowErrors));
    mUI.mActionShowWarnings->setChecked(types->isShown(ShowTypes::ShowWarnings));
    mUI.mActionShowPortability->setChecked(types->isShown(ShowTypes::ShowPortability));
    mUI.mActionShowPerformance->setChecked(types->isShown(ShowTypes::ShowPerformance));
    mUI.mActionShowInformation->setChecked(types->isShown(ShowTypes::ShowInformation));

    const bool stdCpp03 = mSettings->value(SETTINGS_STD_CPP03, false).toBool();
    mUI.mActionCpp03->setChecked(stdCpp03);
    const bool stdCpp11 = mSettings->value(SETTINGS_STD_CPP11, true).toBool();
    mUI.mActionCpp11->setChecked(stdCpp11 || !stdCpp03);
    const bool stdC89 = mSettings->value(SETTINGS_STD_C89, false).toBool();
    mUI.mActionC89->setChecked(stdC89);
    const bool stdC11 = mSettings->value(SETTINGS_STD_C11, false).toBool();
    mUI.mActionC11->setChecked(stdC11);
    const bool stdC99 = mSettings->value(SETTINGS_STD_C99, true).toBool();
    mUI.mActionC99->setChecked(stdC99 || (!stdC89 && !stdC11));
    const bool stdPosix = mSettings->value(SETTINGS_STD_POSIX, false).toBool();
    mUI.mActionPosix->setChecked(stdPosix);

    // Main window settings
    const bool showMainToolbar = mSettings->value(SETTINGS_TOOLBARS_MAIN_SHOW, true).toBool();
    mUI.mActionToolBarMain->setChecked(showMainToolbar);
    mUI.mToolBarMain->setVisible(showMainToolbar);

    const bool showViewToolbar = mSettings->value(SETTINGS_TOOLBARS_VIEW_SHOW, true).toBool();
    mUI.mActionToolBarView->setChecked(showViewToolbar);
    mUI.mToolBarView->setVisible(showViewToolbar);

    const bool showFilterToolbar = mSettings->value(SETTINGS_TOOLBARS_FILTER_SHOW, true).toBool();
    mUI.mActionToolBarFilter->setChecked(showFilterToolbar);
    mUI.mToolBarFilter->setVisible(showFilterToolbar);

    Settings::Language enforcedLanguage = (Settings::Language)mSettings->value(SETTINGS_ENFORCED_LANGUAGE, 0).toInt();
    if (enforcedLanguage == Settings::CPP)
        mUI.mActionEnforceCpp->setChecked(true);
    else if (enforcedLanguage == Settings::C)
        mUI.mActionEnforceC->setChecked(true);
    else
        mUI.mActionAutoDetectLanguage->setChecked(true);

    bool succeeded = mApplications->loadSettings();
    if (!succeeded) {
        const QString msg = tr("There was a problem with loading the editor application settings.\n\n"
                               "This is probably because the settings were changed between the Cppcheck versions. "
                               "Please check (and fix) the editor application settings, otherwise the editor "
                               "program might not start correctly.");
        QMessageBox msgBox(QMessageBox::Warning,
                           tr("Cppcheck"),
                           msg,
                           QMessageBox::Ok,
                           this);
        msgBox.exec();

    }

}

void MainWindow::saveSettings() const
{
    // Window/dialog sizes
    mSettings->setValue(SETTINGS_WINDOW_WIDTH, size().width());
    mSettings->setValue(SETTINGS_WINDOW_HEIGHT, size().height());
    mSettings->setValue(SETTINGS_WINDOW_MAXIMIZED, isMaximized());

    // Show * states
    mSettings->setValue(SETTINGS_SHOW_STYLE, mUI.mActionShowStyle->isChecked());
    mSettings->setValue(SETTINGS_SHOW_ERRORS, mUI.mActionShowErrors->isChecked());
    mSettings->setValue(SETTINGS_SHOW_WARNINGS, mUI.mActionShowWarnings->isChecked());
    mSettings->setValue(SETTINGS_SHOW_PORTABILITY, mUI.mActionShowPortability->isChecked());
    mSettings->setValue(SETTINGS_SHOW_PERFORMANCE, mUI.mActionShowPerformance->isChecked());
    mSettings->setValue(SETTINGS_SHOW_INFORMATION, mUI.mActionShowInformation->isChecked());

    mSettings->setValue(SETTINGS_STD_CPP03, mUI.mActionCpp03->isChecked());
    mSettings->setValue(SETTINGS_STD_CPP11, mUI.mActionCpp11->isChecked());
    mSettings->setValue(SETTINGS_STD_C89, mUI.mActionC89->isChecked());
    mSettings->setValue(SETTINGS_STD_C99, mUI.mActionC99->isChecked());
    mSettings->setValue(SETTINGS_STD_C11, mUI.mActionC11->isChecked());
    mSettings->setValue(SETTINGS_STD_POSIX, mUI.mActionPosix->isChecked());

    // Main window settings
    mSettings->setValue(SETTINGS_TOOLBARS_MAIN_SHOW, mUI.mToolBarMain->isVisible());
    mSettings->setValue(SETTINGS_TOOLBARS_VIEW_SHOW, mUI.mToolBarView->isVisible());
    mSettings->setValue(SETTINGS_TOOLBARS_FILTER_SHOW, mUI.mToolBarFilter->isVisible());

    if (mUI.mActionEnforceCpp->isChecked())
        mSettings->setValue(SETTINGS_ENFORCED_LANGUAGE, Settings::CPP);
    else if (mUI.mActionEnforceC->isChecked())
        mSettings->setValue(SETTINGS_ENFORCED_LANGUAGE, Settings::C);
    else
        mSettings->setValue(SETTINGS_ENFORCED_LANGUAGE, Settings::None);

    mApplications->saveSettings();

    mSettings->setValue(SETTINGS_LANGUAGE, mTranslation->getCurrentLanguage());
    mUI.mResults->saveSettings(mSettings);
}

void MainWindow::doCheckProject(ImportProject p)
{
    clearResults();

    mIsLogfileLoaded = false;
    if (mProject) {
        std::vector<std::string> v;
        foreach (const QString &s, mProject->getProjectFile()->getExcludedPaths()) {
            v.push_back(s.toStdString());
        }
        p.ignorePaths(v);
    } else {
        enableProjectActions(false);
    }

    mUI.mResults->clear(true);
    mThread->clearFiles();

    mUI.mResults->checkingStarted(p.fileSettings.size());

    QDir inf(mCurrentDirectory);
    const QString checkPath = inf.canonicalPath();
    setPath(SETTINGS_LAST_CHECK_PATH, checkPath);

    checkLockDownUI(); // lock UI while checking

    mUI.mResults->setCheckDirectory(checkPath);
    Settings checkSettings = getCppcheckSettings();
    checkSettings.force = false;

    if (mProject)
        qDebug() << "Checking project file" << mProject->getProjectFile()->getFilename();

    if (!checkSettings.buildDir.empty()) {
        std::list<std::string> sourcefiles;
        AnalyzerInformation::writeFilesTxt(checkSettings.buildDir, sourcefiles, p.fileSettings);
    }

    //mThread->SetCheckProject(true);
    mThread->setProject(p);
    mThread->check(checkSettings, true);
}

void MainWindow::doCheckFiles(const QStringList &files)
{
    if (files.isEmpty()) {
        return;
    }
    clearResults();

    mIsLogfileLoaded = false;
    FileList pathList;
    pathList.addPathList(files);
    if (mProject) {
        pathList.addExcludeList(mProject->getProjectFile()->getExcludedPaths());
    } else {
        enableProjectActions(false);
    }
    QStringList fileNames = pathList.getFileList();

    mUI.mResults->clear(true);
    mThread->clearFiles();

    if (fileNames.isEmpty()) {
        QMessageBox msg(QMessageBox::Warning,
                        tr("Cppcheck"),
                        tr("No suitable files found to check!"),
                        QMessageBox::Ok,
                        this);
        msg.exec();
        return;
    }

    mUI.mResults->checkingStarted(fileNames.count());

    mThread->setFiles(fileNames);
    QDir inf(mCurrentDirectory);
    const QString checkPath = inf.canonicalPath();
    setPath(SETTINGS_LAST_CHECK_PATH, checkPath);

    checkLockDownUI(); // lock UI while checking

    mUI.mResults->setCheckDirectory(checkPath);
    Settings checkSettings = getCppcheckSettings();

    if (mProject)
        qDebug() << "Checking project file" << mProject->getProjectFile()->getFilename();

    if (!checkSettings.buildDir.empty()) {
        std::list<std::string> sourcefiles;
        foreach (QString s, fileNames)
            sourcefiles.push_back(s.toStdString());
        AnalyzerInformation::writeFilesTxt(checkSettings.buildDir, sourcefiles, checkSettings.project.fileSettings);
    }

    mThread->setCheckFiles(true);
    mThread->check(checkSettings, true);
}

void MainWindow::checkCode(const QString& code, const QString& filename)
{
    // Initialize dummy ThreadResult as ErrorLogger
    ThreadResult result;
    result.setFiles(QStringList(filename));
    connect(&result, SIGNAL(progress(int, const QString&)),
            mUI.mResults, SLOT(progress(int, const QString&)));
    connect(&result, SIGNAL(error(const ErrorItem &)),
            mUI.mResults, SLOT(error(const ErrorItem &)));
    connect(&result, SIGNAL(log(const QString &)),
            this, SLOT(log(const QString &)));
    connect(&result, SIGNAL(debugError(const ErrorItem &)),
            this, SLOT(debugError(const ErrorItem &)));

    // Create CppCheck instance
    CppCheck cppcheck(result, true);
    cppcheck.settings() = getCppcheckSettings();

    // Check
    checkLockDownUI();
    clearResults();
    mUI.mResults->checkingStarted(1);
    cppcheck.check(filename.toStdString(), code.toStdString());
    checkDone();
}

QStringList MainWindow::selectFilesToCheck(QFileDialog::FileMode mode)
{
    if (mProject) {
        QMessageBox msgBox(this);
        msgBox.setWindowTitle(tr("Cppcheck"));
        const QString msg(tr("You must close the project file before selecting new files or directories!"));
        msgBox.setText(msg);
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.exec();
        return QStringList();
    }

    QStringList selected;

    // NOTE: we use QFileDialog::getOpenFileNames() and
    // QFileDialog::getExistingDirectory() because they show native Windows
    // selection dialog which is a lot more usable than Qt:s own dialog.
    if (mode == QFileDialog::ExistingFiles) {

        selected = QFileDialog::getOpenFileNames(this,
                   tr("Select files to check"),
                   getPath(SETTINGS_LAST_CHECK_PATH),
                   tr("C/C++ Source, Compile database, Visual Studio (%1 %2 *.sln *.vcxproj)")
                   .arg(FileList::getDefaultFilters().join(" "))
                   .arg(compile_commands_json));
        if (selected.isEmpty())
            mCurrentDirectory.clear();
        else {
            QFileInfo inf(selected[0]);
            mCurrentDirectory = inf.absolutePath();
        }
        formatAndSetTitle();
    } else if (mode == QFileDialog::DirectoryOnly) {
        QString dir = QFileDialog::getExistingDirectory(this,
                      tr("Select directory to check"),
                      getPath(SETTINGS_LAST_CHECK_PATH));
        if (!dir.isEmpty()) {
            qDebug() << "Setting current directory to: " << dir;
            mCurrentDirectory = dir;
            selected.append(dir);
            dir = QDir::toNativeSeparators(dir);
            formatAndSetTitle(dir);
        }
    }

    setPath(SETTINGS_LAST_CHECK_PATH, mCurrentDirectory);

    return selected;
}

void MainWindow::checkFiles()
{
    QStringList selected = selectFilesToCheck(QFileDialog::ExistingFiles);

    const QString file0 = (selected.size() ? selected[0].toLower() : "");
    if (file0.endsWith(".sln") || file0.endsWith(".vcxproj") || file0.endsWith(compile_commands_json)) {
        ImportProject p;
        p.import(selected[0].toStdString());

        if (file0.endsWith(".sln")) {
            QStringList configs;
            for (std::list<ImportProject::FileSettings>::const_iterator it = p.fileSettings.begin(); it != p.fileSettings.end(); ++it) {
                const QString cfg(QString::fromStdString(it->cfg));
                if (!configs.contains(cfg))
                    configs.push_back(cfg);
            }
            configs.sort();

            bool ok = false;
            const QString cfg = QInputDialog::getItem(this, tr("Select configuration"), tr("Select the configuration that will be checked"), configs, 0, false, &ok);
            if (!ok)
                return;
            p.ignoreOtherConfigs(cfg.toStdString());
        }

        doCheckProject(p);
        return;
    }

    doCheckFiles(selected);
}

void MainWindow::checkDirectory()
{
    QStringList dir = selectFilesToCheck(QFileDialog::DirectoryOnly);
    if (dir.isEmpty())
        return;

    QDir checkDir(dir[0]);
    QStringList filters;
    filters << "*.cppcheck";
    checkDir.setFilter(QDir::Files | QDir::Readable);
    checkDir.setNameFilters(filters);
    QStringList projFiles = checkDir.entryList();
    if (!projFiles.empty()) {
        if (projFiles.size() == 1) {
            // If one project file found, suggest loading it
            QMessageBox msgBox(this);
            msgBox.setWindowTitle(tr("Cppcheck"));
            const QString msg(tr("Found project file: %1\n\nDo you want to "
                                 "load this project file instead?").arg(projFiles[0]));
            msgBox.setText(msg);
            msgBox.setIcon(QMessageBox::Warning);
            msgBox.addButton(QMessageBox::Yes);
            msgBox.addButton(QMessageBox::No);
            msgBox.setDefaultButton(QMessageBox::Yes);
            int dlgResult = msgBox.exec();
            if (dlgResult == QMessageBox::Yes) {
                QString path = checkDir.canonicalPath();
                if (!path.endsWith("/"))
                    path += "/";
                path += projFiles[0];
                loadProjectFile(path);
            } else {
                doCheckFiles(dir);
            }
        } else {
            // If multiple project files found inform that there are project
            // files also available.
            QMessageBox msgBox(this);
            msgBox.setWindowTitle(tr("Cppcheck"));
            const QString msg(tr("Found project files from the directory.\n\n"
                                 "Do you want to proceed checking without "
                                 "using any of these project files?"));
            msgBox.setText(msg);
            msgBox.setIcon(QMessageBox::Warning);
            msgBox.addButton(QMessageBox::Yes);
            msgBox.addButton(QMessageBox::No);
            msgBox.setDefaultButton(QMessageBox::Yes);
            int dlgResult = msgBox.exec();
            if (dlgResult == QMessageBox::Yes) {
                doCheckFiles(dir);
            }
        }
    } else {
        doCheckFiles(dir);
    }
}

void MainWindow::addIncludeDirs(const QStringList &includeDirs, Settings &result)
{
    QString dir;
    foreach (dir, includeDirs) {
        QString incdir;
        if (!QDir::isAbsolutePath(dir))
            incdir = mCurrentDirectory + "/";
        incdir += dir;
        incdir = QDir::cleanPath(incdir);

        // include paths must end with '/'
        if (!incdir.endsWith("/"))
            incdir += "/";
        result.includePaths.push_back(incdir.toStdString());
    }
}

Library::Error MainWindow::loadLibrary(Library *library, QString filename)
{
    Library::Error ret;

    // Try to load the library from the project folder..
    if (mProject) {
        QString path = QFileInfo(mProject->getProjectFile()->getFilename()).canonicalPath();
        ret = library->load(NULL, (path+"/"+filename).toLatin1());
        if (ret.errorcode != Library::ErrorCode::FILE_NOT_FOUND)
            return ret;
    }

    // Try to load the library from the application folder..
    const QString appPath = QFileInfo(QCoreApplication::applicationFilePath()).canonicalPath();
    ret = library->load(NULL, (appPath+"/"+filename).toLatin1());
    if (ret.errorcode != Library::ErrorCode::FILE_NOT_FOUND)
        return ret;
    ret = library->load(NULL, (appPath+"/cfg/"+filename).toLatin1());
    if (ret.errorcode != Library::ErrorCode::FILE_NOT_FOUND)
        return ret;

#ifdef CFGDIR
    // Try to load the library from CFGDIR..
    const QString cfgdir = CFGDIR;
    if (!cfgdir.isEmpty()) {
        ret = library->load(NULL, (cfgdir+"/"+filename).toLatin1());
        if (ret.errorcode != Library::ErrorCode::FILE_NOT_FOUND)
            return ret;
        ret = library->load(NULL, (cfgdir+"/cfg/"+filename).toLatin1());
        if (ret.errorcode != Library::ErrorCode::FILE_NOT_FOUND)
            return ret;
    }
#endif

    // Try to load the library from the cfg subfolder..
    const QString datadir = mSettings->value("DATADIR", QString()).toString();
    if (!datadir.isEmpty()) {
        ret = library->load(NULL, (datadir+"/"+filename).toLatin1());
        if (ret.errorcode != Library::ErrorCode::FILE_NOT_FOUND)
            return ret;
        ret = library->load(NULL, (datadir+"/cfg/"+filename).toLatin1());
        if (ret.errorcode != Library::ErrorCode::FILE_NOT_FOUND)
            return ret;
    }

    return ret;
}

bool MainWindow::tryLoadLibrary(Library *library, QString filename)
{
    const Library::Error error = loadLibrary(library, filename);
    if (error.errorcode != Library::ErrorCode::OK) {
        if (error.errorcode == Library::UNKNOWN_ELEMENT) {
            QMessageBox::information(this, tr("Information"), tr("The library '%1' contains unknown elements:\n%2").arg(filename).arg(error.reason.c_str()));
            return true;
        }

        QString errmsg;
        switch (error.errorcode) {
        case Library::ErrorCode::OK:
            break;
        case Library::ErrorCode::FILE_NOT_FOUND:
            errmsg = tr("File not found");
            break;
        case Library::ErrorCode::BAD_XML:
            errmsg = tr("Bad XML");
            break;
        case Library::ErrorCode::MISSING_ATTRIBUTE:
            errmsg = tr("Missing attribute");
            break;
        case Library::ErrorCode::BAD_ATTRIBUTE_VALUE:
            errmsg = tr("Bad attribute value");
            break;
        case Library::ErrorCode::UNSUPPORTED_FORMAT:
            errmsg = tr("Unsupported format");
            break;
        case Library::ErrorCode::DUPLICATE_PLATFORM_TYPE:
            errmsg = tr("Duplicate platform type");
            break;
        case Library::ErrorCode::PLATFORM_TYPE_REDEFINED:
            errmsg = tr("Platform type redefined");
            break;
        case Library::ErrorCode::UNKNOWN_ELEMENT:
            errmsg = tr("Unknown element");
            break;
        default:
            errmsg = tr("Unknown issue");
            break;
        }
        if (!error.reason.empty())
            errmsg += " '" + QString::fromStdString(error.reason) + "'";
        QMessageBox::information(this, tr("Information"), tr("Failed to load the selected library '%1'.\n%2").arg(filename).arg(errmsg));
        return false;
    }
    return true;
}

Settings MainWindow::getCppcheckSettings()
{
    saveSettings(); // Save settings

    Settings result;

    // If project file loaded, read settings from it
    if (mProject) {
        ProjectFile *pfile = mProject->getProjectFile();
        QStringList dirs = pfile->getIncludeDirs();
        addIncludeDirs(dirs, result);

        const QStringList defines = pfile->getDefines();
        foreach (QString define, defines) {
            if (!result.userDefines.empty())
                result.userDefines += ";";
            result.userDefines += define.toStdString();
        }

        const QStringList libraries = pfile->getLibraries();
        foreach (QString library, libraries) {
            const QString filename = library + ".cfg";
            tryLoadLibrary(&result.library, filename);
        }

        const QStringList suppressions = pfile->getSuppressions();
        foreach (QString suppression, suppressions) {
            result.nomsg.addSuppressionLine(suppression.toStdString());
        }

        // Only check the given -D configuration
        if (!defines.isEmpty())
            result.maxConfigs = 1;

        QString buildDir = pfile->getBuildDir();
        if (!buildDir.isEmpty()) {
            QString prjpath = QFileInfo(pfile->getFilename()).absolutePath();
            result.buildDir = (prjpath + '/' + buildDir).toStdString();
        }
    }

    // Include directories (and files) are searched in listed order.
    // Global include directories must be added AFTER the per project include
    // directories so per project include directories can override global ones.
    const QString globalIncludes = mSettings->value(SETTINGS_GLOBAL_INCLUDE_PATHS).toString();
    if (!globalIncludes.isEmpty()) {
        QStringList includes = globalIncludes.split(";");
        addIncludeDirs(includes, result);
    }

    result.addEnabled("warning");
    result.addEnabled("style");
    result.addEnabled("performance");
    result.addEnabled("portability");
    result.addEnabled("information");
    result.addEnabled("missingInclude");
    if (!result.buildDir.empty())
        result.addEnabled("unusedFunction");
    result.debug = false;
    result.debugwarnings = mSettings->value(SETTINGS_SHOW_DEBUG_WARNINGS, false).toBool();
    result.quiet = false;
    result.verbose = true;
    result.force = mSettings->value(SETTINGS_CHECK_FORCE, 1).toBool();
    result.xml = false;
    result.jobs = mSettings->value(SETTINGS_CHECK_THREADS, 1).toInt();
    result.inlineSuppressions = mSettings->value(SETTINGS_INLINE_SUPPRESSIONS, false).toBool();
    result.inconclusive = mSettings->value(SETTINGS_INCONCLUSIVE_ERRORS, false).toBool();
    result.platformType = (Settings::PlatformType) mSettings->value(SETTINGS_CHECKED_PLATFORM, 0).toInt();
    result.standards.cpp = mSettings->value(SETTINGS_STD_CPP11, true).toBool() ? Standards::CPP11 : Standards::CPP03;
    result.standards.c = mSettings->value(SETTINGS_STD_C99, true).toBool() ? Standards::C99 : (mSettings->value(SETTINGS_STD_C11, false).toBool() ? Standards::C11 : Standards::C89);
    result.standards.posix = mSettings->value(SETTINGS_STD_POSIX, false).toBool();
    result.enforcedLang = (Settings::Language)mSettings->value(SETTINGS_ENFORCED_LANGUAGE, 0).toInt();

    const bool std = tryLoadLibrary(&result.library, "std.cfg");
    bool posix = true;
    if (result.standards.posix)
        posix = tryLoadLibrary(&result.library, "posix.cfg");
    bool windows = true;
    if (result.platformType == Settings::Win32A || result.platformType == Settings::Win32W || result.platformType == Settings::Win64)
        windows = tryLoadLibrary(&result.library, "windows.cfg");

    if (!std || !posix || !windows)
        QMessageBox::critical(this, tr("Error"), tr("Failed to load %1. Your Cppcheck installation is broken. You can use --data-dir=<directory> at the command line to specify where this file is located. Please note that --data-dir is supposed to be used by installation scripts and therefore the GUI does not start when it is used, all that happens is that the setting is configured.").arg(!std ? "std.cfg" : !posix ? "posix.cfg" : "windows.cfg"));

    if (result.jobs <= 1) {
        result.jobs = 1;
    }

    result.terminate(false);

    return result;
}

void MainWindow::checkDone()
{
    if (mExiting) {
        close();
        return;
    }

    mUI.mResults->checkingFinished();
    enableCheckButtons(true);
    mUI.mActionSettings->setEnabled(true);
    mUI.mActionOpenXML->setEnabled(true);
    if (mProject) {
        enableProjectActions(true);
    } else if (mIsLogfileLoaded) {
        mUI.mActionRecheckModified->setEnabled(false);
        mUI.mActionRecheckAll->setEnabled(false);
    }
    enableProjectOpenActions(true);
    mPlatformActions->setEnabled(true);
    mCStandardActions->setEnabled(true);
    mCppStandardActions->setEnabled(true);
    mSelectLanguageActions->setEnabled(true);
    mUI.mActionPosix->setEnabled(true);
    if (mScratchPad)
        mScratchPad->setEnabled(true);

    if (mUI.mResults->hasResults()) {
        mUI.mActionClearResults->setEnabled(true);
        mUI.mActionSave->setEnabled(true);
        mUI.mActionPrint->setEnabled(true);
        mUI.mActionPrintPreview->setEnabled(true);
    }

    for (int i = 0; i < MaxRecentProjects + 1; i++) {
        if (mRecentProjectActs[i] != NULL)
            mRecentProjectActs[i]->setEnabled(true);
    }

    // Notify user - if the window is not active - that check is ready
    QApplication::alert(this, 3000);
    if (mSettings->value(SETTINGS_SHOW_STATISTICS, false).toBool())
        showStatistics();
}

void MainWindow::checkLockDownUI()
{
    enableCheckButtons(false);
    mUI.mActionSettings->setEnabled(false);
    mUI.mActionOpenXML->setEnabled(false);
    enableProjectActions(false);
    enableProjectOpenActions(false);
    mPlatformActions->setEnabled(false);
    mCStandardActions->setEnabled(false);
    mCppStandardActions->setEnabled(false);
    mSelectLanguageActions->setEnabled(false);
    mUI.mActionPosix->setEnabled(false);
    if (mScratchPad)
        mScratchPad->setEnabled(false);

    for (int i = 0; i < MaxRecentProjects + 1; i++) {
        if (mRecentProjectActs[i] != NULL)
            mRecentProjectActs[i]->setEnabled(false);
    }
}

void MainWindow::programSettings()
{
    SettingsDialog dialog(mApplications, mTranslation, this);
    if (dialog.exec() == QDialog::Accepted) {
        dialog.saveSettingValues();
        mUI.mResults->updateSettings(dialog.showFullPath(),
                                     dialog.saveFullPath(),
                                     dialog.saveAllErrors(),
                                     dialog.showNoErrorsMessage(),
                                     dialog.showErrorId(),
                                     dialog.showInconclusive());
        const QString newLang = mSettings->value(SETTINGS_LANGUAGE, "en").toString();
        setLanguage(newLang);
    }
}

void MainWindow::reCheckModified()
{
    reCheck(false);
}

void MainWindow::reCheckAll()
{
    reCheck(true);
}

void MainWindow::reCheckSelected(QStringList files, bool all)
{
    if (files.empty())
        return;
    if (mThread->isChecking())
        return;

    // Clear details, statistics and progress
    mUI.mResults->clear(false);
    for (int i = 0; i < files.size(); ++i)
        mUI.mResults->clearRecheckFile(files[i]);

    mCurrentDirectory = mUI.mResults->getCheckDirectory();
    FileList pathList;
    pathList.addPathList(files);
    if (mProject)
        pathList.addExcludeList(mProject->getProjectFile()->getExcludedPaths());
    QStringList fileNames = pathList.getFileList();
    checkLockDownUI(); // lock UI while checking
    mUI.mResults->checkingStarted(fileNames.size());
    mThread->setCheckFiles(fileNames);

    // Saving last check start time, otherwise unchecked modified files will not be
    // considered in "Modified Files Check"  performed after "Selected Files Check"
    // TODO: Should we store per file CheckStartTime?
    QDateTime saveCheckStartTime = mThread->getCheckStartTime();
    mThread->check(getCppcheckSettings(), all);
    mThread->setCheckStartTime(saveCheckStartTime);
}

void MainWindow::reCheck(bool all)
{
    const QStringList files = mThread->getReCheckFiles(all);
    if (files.empty())
        return;

    // Clear details, statistics and progress
    mUI.mResults->clear(all);

    // Clear results for changed files
    for (int i = 0; i < files.size(); ++i)
        mUI.mResults->clear(files[i]);

    checkLockDownUI(); // lock UI while checking
    mUI.mResults->checkingStarted(files.size());

    if (mProject)
        qDebug() << "Rechecking project file" << mProject->getProjectFile()->getFilename();

    mThread->setCheckFiles(all);
    mThread->check(getCppcheckSettings(), all);
}

void MainWindow::clearResults()
{
    mUI.mResults->clear(true);
    mUI.mActionClearResults->setEnabled(false);
    mUI.mActionSave->setEnabled(false);
    mUI.mActionPrint->setEnabled(false);
    mUI.mActionPrintPreview->setEnabled(false);
}

void MainWindow::openResults()
{
    if (mUI.mResults->hasResults()) {
        QMessageBox msgBox(this);
        msgBox.setWindowTitle(tr("Cppcheck"));
        const QString msg(tr("Current results will be cleared.\n\n"
                             "Opening a new XML file will clear current results."
                             "Do you want to proceed?"));
        msgBox.setText(msg);
        msgBox.setIcon(QMessageBox::Warning);
        msgBox.addButton(QMessageBox::Yes);
        msgBox.addButton(QMessageBox::No);
        msgBox.setDefaultButton(QMessageBox::Yes);
        int dlgResult = msgBox.exec();
        if (dlgResult == QMessageBox::No) {
            return;
        }
    }

    QString selectedFilter;
    const QString filter(tr("XML files (*.xml)"));
    QString selectedFile = QFileDialog::getOpenFileName(this,
                           tr("Open the report file"),
                           getPath(SETTINGS_LAST_RESULT_PATH),
                           filter,
                           &selectedFilter);

    if (!selectedFile.isEmpty()) {
        loadResults(selectedFile);
    }
}

void MainWindow::loadResults(const QString selectedFile)
{
    if (!selectedFile.isEmpty()) {
        if (mProject)
            closeProjectFile();
        mIsLogfileLoaded = true;
        mUI.mResults->clear(true);
        mUI.mActionRecheckModified->setEnabled(false);
        mUI.mActionRecheckAll->setEnabled(false);
        mUI.mResults->readErrorsXml(selectedFile);
        setPath(SETTINGS_LAST_RESULT_PATH, selectedFile);
    }
}

void MainWindow::loadResults(const QString selectedFile, const QString sourceDirectory)
{
    loadResults(selectedFile);
    mUI.mResults->setCheckDirectory(sourceDirectory);
}

void MainWindow::enableCheckButtons(bool enable)
{
    mUI.mActionStop->setEnabled(!enable);
    mUI.mActionCheckFiles->setEnabled(enable);

    if (!enable || mThread->hasPreviousFiles()) {
        mUI.mActionRecheckModified->setEnabled(enable);
        mUI.mActionRecheckAll->setEnabled(enable);
    }

    mUI.mActionCheckDirectory->setEnabled(enable);
}

void MainWindow::showStyle(bool checked)
{
    mUI.mResults->showResults(ShowTypes::ShowStyle, checked);
}

void MainWindow::showErrors(bool checked)
{
    mUI.mResults->showResults(ShowTypes::ShowErrors, checked);
}

void MainWindow::showWarnings(bool checked)
{
    mUI.mResults->showResults(ShowTypes::ShowWarnings, checked);
}

void MainWindow::showPortability(bool checked)
{
    mUI.mResults->showResults(ShowTypes::ShowPortability, checked);
}

void MainWindow::showPerformance(bool checked)
{
    mUI.mResults->showResults(ShowTypes::ShowPerformance, checked);
}

void MainWindow::showInformation(bool checked)
{
    mUI.mResults->showResults(ShowTypes::ShowInformation, checked);
}

void MainWindow::checkAll()
{
    toggleAllChecked(true);
}

void MainWindow::uncheckAll()
{
    toggleAllChecked(false);
}

void MainWindow::closeEvent(QCloseEvent *event)
{
    // Check that we aren't checking files
    if (!mThread->isChecking()) {
        saveSettings();
        event->accept();
    } else {
        const QString text(tr("Checking is running.\n\n" \
                              "Do you want to stop the checking and exit Cppcheck?"));

        QMessageBox msg(QMessageBox::Warning,
                        tr("Cppcheck"),
                        text,
                        QMessageBox::Yes | QMessageBox::No,
                        this);

        msg.setDefaultButton(QMessageBox::No);
        int rv = msg.exec();
        if (rv == QMessageBox::Yes) {
            // This isn't really very clean way to close threads but since the app is
            // exiting it doesn't matter.
            mThread->stop();
            saveSettings();
            mExiting = true;
        }
        event->ignore();
    }
}

void MainWindow::toggleAllChecked(bool checked)
{
    mUI.mActionShowStyle->setChecked(checked);
    showStyle(checked);
    mUI.mActionShowErrors->setChecked(checked);
    showErrors(checked);
    mUI.mActionShowWarnings->setChecked(checked);
    showWarnings(checked);
    mUI.mActionShowPortability->setChecked(checked);
    showPortability(checked);
    mUI.mActionShowPerformance->setChecked(checked);
    showPerformance(checked);
    mUI.mActionShowInformation->setChecked(checked);
    showInformation(checked);
}

void MainWindow::about()
{
    AboutDialog *dlg = new AboutDialog(CppCheck::version(), CppCheck::extraVersion(), this);
    dlg->exec();
}

void MainWindow::showLicense()
{
    FileViewDialog *dlg = new FileViewDialog(":COPYING", tr("License"), this);
    dlg->resize(570, 400);
    dlg->exec();
}

void MainWindow::showAuthors()
{
    FileViewDialog *dlg = new FileViewDialog(":AUTHORS", tr("Authors"), this);
    dlg->resize(350, 400);
    dlg->exec();
}

void MainWindow::performSelectedFilesCheck(QStringList selectedFilesList)
{
    reCheckSelected(selectedFilesList, true);
}

void MainWindow::save()
{
    QString selectedFilter;
    const QString filter(tr("XML files version 2 (*.xml);;XML files version 1 (*.xml);;Text files (*.txt);;CSV files (*.csv)"));
    QString selectedFile = QFileDialog::getSaveFileName(this,
                           tr("Save the report file"),
                           getPath(SETTINGS_LAST_RESULT_PATH),
                           filter,
                           &selectedFilter);

    if (!selectedFile.isEmpty()) {
        Report::Type type = Report::TXT;
        if (selectedFilter == tr("XML files version 1 (*.xml)")) {
            QMessageBox msgBox(QMessageBox::Icon::Warning, tr("Deprecated XML format"), tr("XML format 1 is deprecated and will be removed in cppcheck 1.81."), QMessageBox::StandardButton::Ok);
            msgBox.exec();

            type = Report::XML;
            if (!selectedFile.endsWith(".xml", Qt::CaseInsensitive))
                selectedFile += ".xml";
        } else if (selectedFilter == tr("XML files version 2 (*.xml)")) {
            type = Report::XMLV2;
            if (!selectedFile.endsWith(".xml", Qt::CaseInsensitive))
                selectedFile += ".xml";
        } else if (selectedFilter == tr("Text files (*.txt)")) {
            type = Report::TXT;
            if (!selectedFile.endsWith(".txt", Qt::CaseInsensitive))
                selectedFile += ".txt";
        } else if (selectedFilter == tr("CSV files (*.csv)")) {
            type = Report::CSV;
            if (!selectedFile.endsWith(".csv", Qt::CaseInsensitive))
                selectedFile += ".csv";
        } else {
            if (selectedFile.endsWith(".xml", Qt::CaseInsensitive))
                type = Report::XML;
            else if (selectedFile.endsWith(".txt", Qt::CaseInsensitive))
                type = Report::TXT;
            else if (selectedFile.endsWith(".csv", Qt::CaseInsensitive))
                type = Report::CSV;
        }

        mUI.mResults->save(selectedFile, type);
        setPath(SETTINGS_LAST_RESULT_PATH, selectedFile);
    }
}

void MainWindow::resultsAdded()
{
}

void MainWindow::toggleMainToolBar()
{
    mUI.mToolBarMain->setVisible(mUI.mActionToolBarMain->isChecked());
}

void MainWindow::toggleViewToolBar()
{
    mUI.mToolBarView->setVisible(mUI.mActionToolBarView->isChecked());
}

void MainWindow::toggleFilterToolBar()
{
    mUI.mToolBarFilter->setVisible(mUI.mActionToolBarFilter->isChecked());
    mLineEditFilter->clear(); // Clearing the filter also disables filtering
}

void MainWindow::formatAndSetTitle(const QString &text)
{
    QString title;
    if (text.isEmpty())
        title = tr("Cppcheck");
    else
        title = QString(tr("Cppcheck - %1")).arg(text);
    setWindowTitle(title);
}

void MainWindow::setLanguage(const QString &code)
{
    const QString currentLang = mTranslation->getCurrentLanguage();
    if (currentLang == code)
        return;

    if (mTranslation->setLanguage(code)) {
        //Translate everything that is visible here
        mUI.retranslateUi(this);
        mUI.mResults->translate();
        delete mLogView;
        mLogView = 0;
    }
}

void MainWindow::aboutToShowViewMenu()
{
    mUI.mActionToolBarMain->setChecked(mUI.mToolBarMain->isVisible());
    mUI.mActionToolBarView->setChecked(mUI.mToolBarView->isVisible());
    mUI.mActionToolBarFilter->setChecked(mUI.mToolBarFilter->isVisible());
}

void MainWindow::stopChecking()
{
    mThread->stop();
    mUI.mResults->disableProgressbar();
}

void MainWindow::openHelpContents()
{
    openOnlineHelp();
}

void MainWindow::openOnlineHelp()
{
    QDesktopServices::openUrl(QUrl(OnlineHelpURL));
}

void MainWindow::openProjectFile()
{
    const QString lastPath = mSettings->value(SETTINGS_LAST_PROJECT_PATH, QString()).toString();
    const QString filter = tr("Project files (*.cppcheck);;All files(*.*)");
    const QString filepath = QFileDialog::getOpenFileName(this,
                             tr("Select Project File"),
                             getPath(SETTINGS_LAST_PROJECT_PATH),
                             filter);

    if (!filepath.isEmpty()) {
        const QFileInfo fi(filepath);
        if (fi.exists() && fi.isFile() && fi.isReadable()) {
            setPath(SETTINGS_LAST_PROJECT_PATH, filepath);
            loadProjectFile(filepath);
        }
    }
}

void MainWindow::showScratchpad()
{
    if (!mScratchPad)
        mScratchPad = new ScratchPad(*this);

    mScratchPad->show();

    if (!mScratchPad->isActiveWindow())
        mScratchPad->activateWindow();
}

void MainWindow::loadProjectFile(const QString &filePath)
{
    QFileInfo inf(filePath);
    const QString filename = inf.fileName();
    formatAndSetTitle(tr("Project:") + QString(" ") + filename);
    addProjectMRU(filePath);

    mIsLogfileLoaded = false;
    mUI.mActionCloseProjectFile->setEnabled(true);
    mUI.mActionEditProjectFile->setEnabled(true);
    delete mProject;
    mProject = new Project(filePath, this);
    checkProject(mProject);
}

void MainWindow::checkProject(Project *project)
{
    if (!project->isOpen()) {
        if (!project->open()) {
            delete mProject;
            mProject = 0;
            return;
        }
    }

    QFileInfo inf(project->getFilename());
    const QString rootpath = project->getProjectFile()->getRootPath();

    // If the root path is not given or is not "current dir", use project
    // file's location directory as root path
    if (rootpath.isEmpty() || rootpath == ".")
        mCurrentDirectory = inf.canonicalPath();
    else if (rootpath.startsWith("."))
        mCurrentDirectory = inf.canonicalPath() + rootpath.mid(1);
    else
        mCurrentDirectory = rootpath;

    if (!project->getProjectFile()->getBuildDir().isEmpty()) {
        QString buildDir = project->getProjectFile()->getBuildDir();
        if (!QDir::isAbsolutePath(buildDir))
            buildDir = mCurrentDirectory + '/' + buildDir;
        if (!QDir(buildDir).exists()) {
            QMessageBox msg(QMessageBox::Critical,
                            tr("Cppcheck"),
                            tr("Build dir '%1' does not exist, create it?").arg(buildDir),
                            QMessageBox::Yes | QMessageBox::No,
                            this);
            if (msg.exec() == QMessageBox::Yes) {
                QDir().mkdir(buildDir);
            }
        }
    }

    if (!project->getProjectFile()->getImportProject().isEmpty()) {
        ImportProject p;
        QString prjfile = inf.canonicalPath() + '/' + project->getProjectFile()->getImportProject();
        p.import(prjfile.toStdString());
        doCheckProject(p);
        return;
    }

    QStringList paths = project->getProjectFile()->getCheckPaths();

    // If paths not given then check the root path (which may be the project
    // file's location, see above). This is to keep the compatibility with
    // old "silent" project file loading when we checked the director where the
    // project file was located.
    if (paths.isEmpty()) {
        paths << mCurrentDirectory;
    }

    // Convert relative paths to absolute paths
    for (int i = 0; i < paths.size(); i++) {
        if (!QDir::isAbsolutePath(paths[i])) {
            QString path = mCurrentDirectory + "/";
            path += paths[i];
            paths[i] = QDir::cleanPath(path);
        }
    }
    doCheckFiles(paths);
}

void MainWindow::newProjectFile()
{
    const QString filter = tr("Project files (*.cppcheck);;All files(*.*)");
    QString filepath = QFileDialog::getSaveFileName(this,
                       tr("Select Project Filename"),
                       getPath(SETTINGS_LAST_PROJECT_PATH),
                       filter);

    if (filepath.isEmpty())
        return;

    setPath(SETTINGS_LAST_PROJECT_PATH, filepath);

    enableProjectActions(true);
    QFileInfo inf(filepath);
    const QString filename = inf.fileName();
    formatAndSetTitle(tr("Project:") + QString(" ") + filename);

    delete mProject;
    mProject = new Project(filepath, this);
    mProject->create();
    if (mProject->edit()) {
        addProjectMRU(filepath);
        checkProject(mProject);
    }
}

void MainWindow::closeProjectFile()
{
    delete mProject;
    mProject = NULL;
    enableProjectActions(false);
    enableProjectOpenActions(true);
    formatAndSetTitle();
}

void MainWindow::editProjectFile()
{
    if (!mProject) {
        QMessageBox msg(QMessageBox::Critical,
                        tr("Cppcheck"),
                        QString(tr("No project file loaded")),
                        QMessageBox::Ok,
                        this);
        msg.exec();
        return;
    }
    if (mProject->edit())
        checkProject(mProject);
}

void MainWindow::showLogView()
{
    if (mLogView == NULL)
        mLogView = new LogView;

    mLogView->show();
    if (!mLogView->isActiveWindow())
        mLogView->activateWindow();
}

void MainWindow::showStatistics()
{
    StatsDialog statsDialog(this);

    // Show a dialog with the previous scan statistics and project information
    if (mProject) {
        statsDialog.setProject(*mProject);
    }
    statsDialog.setPathSelected(mCurrentDirectory);
    statsDialog.setNumberOfFilesScanned(mThread->getPreviousFilesCount());
    statsDialog.setScanDuration(mThread->getPreviousScanDuration() / 1000.0);
    statsDialog.setStatistics(mUI.mResults->getStatistics());

    statsDialog.exec();
}

void MainWindow::showLibraryEditor()
{
    LibraryDialog libraryDialog(this);
    libraryDialog.exec();
}

void MainWindow::log(const QString &logline)
{
    if (mLogView) {
        mLogView->appendLine(logline);
    }
}

void MainWindow::debugError(const ErrorItem &item)
{
    if (mLogView) {
        mLogView->appendLine(item.ToString());
    }
}

void MainWindow::filterResults()
{
    mUI.mResults->filterResults(mLineEditFilter->text());
}

void MainWindow::enableProjectActions(bool enable)
{
    mUI.mActionCloseProjectFile->setEnabled(enable);
    mUI.mActionEditProjectFile->setEnabled(enable);
}

void MainWindow::enableProjectOpenActions(bool enable)
{
    mUI.mActionNewProjectFile->setEnabled(enable);
    mUI.mActionOpenProjectFile->setEnabled(enable);
}

void MainWindow::openRecentProject()
{
    QAction *action = qobject_cast<QAction *>(sender());
    if (action) {
        const QString project = action->data().toString();
        QFileInfo inf(project);
        if (inf.exists()) {
            loadProjectFile(project);
        } else {
            const QString text(tr("The project file\n\n%1\n\n could not be found!\n\n"
                                  "Do you want to remove the file from the recently "
                                  "used projects -list?").arg(project));

            QMessageBox msg(QMessageBox::Warning,
                            tr("Cppcheck"),
                            text,
                            QMessageBox::Yes | QMessageBox::No,
                            this);

            msg.setDefaultButton(QMessageBox::No);
            int rv = msg.exec();
            if (rv == QMessageBox::Yes) {
                removeProjectMRU(project);
            }

        }
    }
}

void MainWindow::updateMRUMenuItems()
{
    for (int i = 0; i < MaxRecentProjects + 1; i++) {
        if (mRecentProjectActs[i] != NULL)
            mUI.mMenuFile->removeAction(mRecentProjectActs[i]);
    }

    QStringList projects = mSettings->value(SETTINGS_MRU_PROJECTS).toStringList();

    // Do a sanity check - remove duplicates and empty or space only items
    int removed = projects.removeDuplicates();
    for (int i = projects.size() - 1; i >= 0; i--) {
        QString text = projects[i].trimmed();
        if (text.isEmpty()) {
            projects.removeAt(i);
            removed++;
        }
    }

    if (removed)
        mSettings->setValue(SETTINGS_MRU_PROJECTS, projects);

    const int numRecentProjects = qMin(projects.size(), (int)MaxRecentProjects);
    for (int i = 0; i < numRecentProjects; i++) {
        const QString filename = QFileInfo(projects[i]).fileName();
        const QString text = QString("&%1 %2").arg(i + 1).arg(filename);
        mRecentProjectActs[i]->setText(text);
        mRecentProjectActs[i]->setData(projects[i]);
        mRecentProjectActs[i]->setVisible(true);
        mUI.mMenuFile->insertAction(mUI.mActionProjectMRU, mRecentProjectActs[i]);
    }

    if (numRecentProjects > 1)
        mRecentProjectActs[numRecentProjects] = mUI.mMenuFile->insertSeparator(mUI.mActionProjectMRU);
}

void MainWindow::addProjectMRU(const QString &project)
{
    QStringList files = mSettings->value(SETTINGS_MRU_PROJECTS).toStringList();
    files.removeAll(project);
    files.prepend(project);
    while (files.size() > MaxRecentProjects)
        files.removeLast();

    mSettings->setValue(SETTINGS_MRU_PROJECTS, files);
    updateMRUMenuItems();
}

void MainWindow::removeProjectMRU(const QString &project)
{
    QStringList files = mSettings->value(SETTINGS_MRU_PROJECTS).toStringList();
    files.removeAll(project);

    mSettings->setValue(SETTINGS_MRU_PROJECTS, files);
    updateMRUMenuItems();
}

void MainWindow::selectPlatform()
{
    QAction *action = qobject_cast<QAction *>(sender());
    if (action) {
        const Settings::PlatformType platform = (Settings::PlatformType) action->data().toInt();
        mSettings->setValue(SETTINGS_CHECKED_PLATFORM, platform);
    }
}
