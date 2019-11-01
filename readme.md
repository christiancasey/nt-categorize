# New Titles

## General Workflow

1. David receives New Titles data (XML)
2. Query missing data from Aleph API
3. Clean up book records
	1. Categorize (perfect this step in separate repo <<LINK>>)
	2. Dedupe
	3. Sort
4. Import to Zotero
	1. Aleph -> ~~BibTeX~~ some python format
	2. Import with pyzotero
5. Build map data
	1. Query missing data
		1. ISAW lookup table
		2. Pleiades
		3. Hathi Trust
6. Connect front end to new data
	1. Build HTML list of books (grouped by category)
	2. Generate Leaflet map (perfect this step in separate repo <<LINK>>)
7. Alert mechanism – reach interested parties
	1. Blog post
	2. Geofence (future project)

## Todo List

- [ ] Create webpage for old data
- [ ] Figure out how we get things online
- [ ] Figure out how to get data from Aleph API
- [ ] Rebuild categorization script
- [ ] Finalize Leaflet map operation
- [ ] Build geofence part
