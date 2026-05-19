# Project: Xay dung tro choi Co Caro bang thua toan Minimax va Alpha-Beta

Du an phat trien tro choi Co Caro doi khang truc tiep (Nguoi vs May), tich hop Tri tue nhan tao dua tren thuat toan tim kiem quyet dinh Minimax va Alpha-Beta Pruning.

# Thanh vien nhom thuc hien

Nguyen Viet Hoang - 23021271

# CaroAI - Bai tap lap trinh giua ky

Chuong trinh cai dat game co Caro nguoi choi dau voi may tinh tren console va giao dien Tkinter. 
 Kich thuoc ban co mac dinh la: 9x9
 Nguoi choi la: `X`, may la: `O`
 Nguoi thang la ben co 4 quan lien tiep theo hang ngang, doc hoac cheo. Chuong trinh khong xet luat chan hai dau, neu Ban co day va khong co nguoi thang thi ket qua la hoa.

## Cau truc thu muc

```text
source_code/
  main.py              # chay game console nguoi choi vs may
  gui.py               # chay giao dien Tkinter
  benchmark.py         # chay thuc nghiem Minimax va Alpha-Beta
  tests.py             # kiem thu nhanh game logic va AI
  caro/
    board.py           # bieu dien ban co, luat choi, kiem tra thang/thua/hoa
    ai.py              # ham danh gia, Minimax, Alpha-Beta, transposition table, thong ke
    gui.py             # giao dien choi co bang Tkinter Canvas
    benchmark.py       # 6 trang thai kiem thu
requirements.txt
README.md
```
## Cach chay

Can Python 3.10 tro len. Du an khong can cai them thu vien ngoai.

Chay giao dien:

```bash
cd source_code
python gui.py
```

Chay game tren console:

```bash
cd source_code
python main.py
```

Chay benchmark:

```bash
cd source_code
python benchmark.py
```

Lenh benchmark se in bang ket qua chi tiet, bang so sanh Minimax voi Alpha-Beta va tao hai file o thu muc goc:

- `benchmark_results.csv`: ket qua tung thuat toan tren tung trang thai.
- `benchmark_comparison.csv`: so sanh cung nuoc di, so trang thai giam duoc va ti le thoi gian.

Chay kiem thu:

```bash
cd source_code
python tests.py
```

## Chuc nang da cai dat

- Ban co toi thieu 9x9, co the nhap kich thuoc lon hon khi bat dau game.
- Nguoi choi va may danh luan phien, khong cho danh vao o da co quan.
- Kiem tra thang khi co 4 quan lien tiep theo 4 huong: ngang, doc, cheo chinh, cheo phu.
- Kiem tra hoa khi ban co day va khong co nguoi thang.
- AI co 2 che do: Minimax va Alpha-Beta pruning.
- Tuy chinh do khoa cua AI thong qua tham so Do Sau (Depth)
- Co giao dien Tkinter Canvas theme toi, cac nut bo tron dang noi, ban co dang o vuong, quan X/O mau ro, to xanh nhe nuoc cuoi, goi y nuoc di va nut di lai luot truoc.
- Co che do so sanh Minimax va Alpha-Beta tren cung trang thai hien tai trong console va giao dien, kem bang so sanh trong GUI.
- Hai thuat toan dung cung ham danh gia, cung do sau va cung thu tu sinh nuoc di khi so sanh.
- Moi nuoc di cua may hien thi: nuoc di, gia tri danh gia, do sau, so trang thai da xet va thoi gian chay.
- Benchmark co 6 trang thai: dau van, giua van, may thang ngay, nguoi sap thang can chan, hai ben cung tan cong va trang thai co nhieu nhanh.

## Ghi chu ve cai dat

De tranh so nhanh qua lon, chuong trinh chi sinh cac nuoc di trong ban kinh 1 o quanh cac quan da danh. Neu ban co dang rong, nuoc di dau tien cua may la o trung tam. Cac nuoc di duoc sap xep uu tien theo kha nang tao chuoi hoac chan chuoi 2, 3, 4 quan, sau do uu tien gan trung tam.

Ham danh gia cong diem cho chuoi tiem nang cua may va tru diem cho chuoi tiem nang cua nguoi:

- May co 4 quan: diem rat lon.
- Nguoi co 4 quan: diem rat nho.
- May co 3 quan, dac biet la chuoi mo hai dau: diem cao.
- Nguoi co 3 quan, dac biet la chuoi mo hai dau: diem am lon de uu tien chan.
- Chuoi 2 va 1 quan co diem nho hon.
- Nuoc tao hai moi de doa tro len duoc cong/tru diem nhu mot fork.

Minimax va Alpha-Beta dung transposition table trong moi lan tim nuoc di. Khoa cache gom trang thai ban co, do sau con lai va luot MAX/MIN; voi Alpha-Beta chi luu cac nhanh da duyet day du de tranh dung nham gia tri sau cat nhanh.
