export class Paginator {
  constructor(items = [], pageSize = 10) {
    this.items = items;
    this.pageSize = pageSize;
    this.currentPage = 0;
  }

  setItems(items) {
    this.items = items;
    this.currentPage = 0;
  }

  get totalPages() {
    return Math.ceil(this.items.length / this.pageSize) || 1;
  }

  get pageItems() {
    const start = this.currentPage * this.pageSize;
    return this.items.slice(start, start + this.pageSize);
  }

  canPrev() {
    return this.currentPage > 0;
  }

  canNext() {
    return this.currentPage < this.totalPages - 1;
  }

  prev() {
    if (this.canPrev()) {
      this.currentPage -= 1;
    }
  }

  next() {
    if (this.canNext()) {
      this.currentPage += 1;
    }
  }
}
