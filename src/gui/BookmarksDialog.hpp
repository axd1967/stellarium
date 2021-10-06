/*
 * Stellarium
 * 
 * Copyright (C) 2016 Alexander Wolf
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Suite 500, Boston, MA  02110-1335, USA.
*/

#ifndef BOOKMARKSDIALOG_HPP
#define BOOKMARKSDIALOG_HPP

#include <QObject>
#include <QStandardItemModel>
#include <QMap>
#include <QDir>
#include <QUuid>

#include "StelDialog.hpp"
#include "StelCore.hpp"

class Ui_bookmarksDialogForm;

struct bookmark
{
	QString name;
	QString nameI18n;
	QString ra;
	QString dec;
	bool isVisibleMarker;
	QString jd;
	QString location;
	double fov;
};
Q_DECLARE_METATYPE(bookmark)

class BookmarksDialog : public StelDialog
{
	Q_OBJECT
	Q_PROPERTY(bool flagHighlighting READ getFlagHighlighting WRITE setHighlighting NOTIFY flagHighlightingChanged)

public:
	BookmarksDialog(QObject* parent);
	virtual ~BookmarksDialog() Q_DECL_OVERRIDE;

signals:
	void flagHighlightingChanged();

public slots:
	void retranslate() Q_DECL_OVERRIDE;

	void setHighlighting(bool b);
	bool getFlagHighlighting() const { return flagHighlighting; }

protected:
        //! Initialize the dialog widgets and connect the signals/slots.
	virtual void createDialogContent() Q_DECL_OVERRIDE;
	Ui_bookmarksDialogForm *ui;

private slots:
	void addBookmarkButtonPressed();
	void removeBookmarkButtonPressed();
	void goToBookmarkButtonPressed();
	void clearBookmarksButtonPressed();

	void highlightBookmarksButtonPressed();
	void clearHighlightsButtonPressed();
	void toggleHighlights();

	void exportBookmarks();
	void importBookmarks();

	void selectCurrentBookmark(const QModelIndex &modelIdx);

private:
	enum BookmarksColumns {
		ColumnUUID,	//! UUID of bookmark
		ColumnName,	//! name or designation of object
		ColumnNameI18n,	//! Localized name of object
		ColumnDate,	//! date and time (optional)
		ColumnLocation,	//! location (optional)
		ColumnCount	//! total number of columns
	};
	QStandardItemModel * bookmarksListModel;

	class StelCore* core;
	class StelObjectMgr* objectMgr;
	class LabelMgr* labelMgr;

	QString bookmarksJsonPath;
	QHash<QString, bookmark> bookmarksCollection;
	QList<int> highlightLabelIDs;

	bool flagHighlighting;

	//! Update header names for bookmarks table
	void setBookmarksHeaderNames();

	void addModelRow(int number, QString uuid, QString name, QString nameI18n = "", QString date = "", QString Location = "");

	void loadBookmarks();
	void saveBookmarks() const;
	void goToBookmark(QString uuid);

};


#endif // BOOKMARKSDIALOG_HPP
