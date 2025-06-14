import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Storage } from '@ionic/storage-angular';
import { LoadingController, ModalController } from '@ionic/angular';

import { OnlineStatusService } from '../services/online.service';
import { PhotoService, UserPhoto } from '../services/photo.service';
import { ChooseViolationModalComponent } from '../choose-violation-modal/choose-violation-modal.component';
import { ConfirmViolationDetailsModalComponent } from '../confirm-violation-details-modal/confirm-violation-details-modal.component';
import { best_match } from '../violation-matcher/violation-matcher';

async function compressJpegDataUrl(
  dataUrl: string,
  quality: number,
): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Canvas context not available'));
        return;
      }
      ctx.drawImage(img, 0, 0);
      const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
      resolve(compressedDataUrl);
    };
    img.onerror = (error) => {
      reject(error);
    };
    img.src = dataUrl;
  });
}

@Component({
  selector: 'app-violation-detail',
  templateUrl: './violation-detail.page.html',
  styleUrls: ['./violation-detail.page.scss'],
  standalone: false,
})
export class ViolationDetailPage implements OnInit {
  violationId: number | null = null;
  violationData: any = null;
  violationImageLoaded: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private loadingCtrl: LoadingController,
    public changeDetectorRef: ChangeDetectorRef,
    private modalCtrl: ModalController,
    private storage: Storage,
    public photos: PhotoService,
    public onlineStatus: OnlineStatusService,
  ) {}

  async selectVehicle(index: number) {
    this.violationData.vehicle = this.violationData.raw.vehicles[index];
    this.storage.set('violation-' + this.violationId, this.violationData);
    this.changeDetectorRef.detectChanges();
  }

  async drawHitBoxes() {
    if (!this.violationData.raw!.vehicles) {
      return;
    }
    const image = document.getElementById('imagePreview') as HTMLImageElement;
    const shadowRoot = image.shadowRoot;
    const shadowImage = shadowRoot!.querySelector('img');
    const rect = shadowImage!.getBoundingClientRect();

    shadowRoot!.getElementById('imageOverlay')?.remove();

    const overlayDiv = document.createElement('div');
    overlayDiv.id = 'imageOverlay';
    overlayDiv.className = 'imageOverlay';
    overlayDiv.style.position = 'absolute';
    overlayDiv.style.width = rect.width + 'px';
    overlayDiv.style.height = rect.height + 'px';
    shadowImage!.insertAdjacentElement('beforebegin', overlayDiv);

    const scale =
      (shadowImage!.width / shadowImage!.naturalWidth +
        shadowImage!.height / shadowImage!.naturalHeight) /
      2;

    this.violationData.raw.vehicles.forEach((element: any, index: number) => {
      if (element.vehicle) {
        const box = document.createElement('a');
        box.style.position = 'absolute';
        box.style.zIndex = `${15 - index}`;
        box.style.border = '3px solid lime';
        box.style.left = element.vehicle.box.xmin * scale + 'px';
        box.style.top = element.vehicle.box.ymin * scale + 'px';
        box.addEventListener('click', (event) => {
          this.selectVehicle(index);
        });
        box.style.width =
          (element.vehicle.box.xmax - element.vehicle.box.xmin) * scale + 'px';
        box.style.height =
          (element.vehicle.box.ymax - element.vehicle.box.ymin) * scale + 'px';
        overlayDiv.appendChild(box);
      }
      if (element.plate) {
        const box = document.createElement('div');
        box.style.position = 'absolute';
        box.style.zIndex = '8';
        box.style.border = '2px solid yellow';
        box.style.left =
          (element.plate.box.xmin / shadowImage!.naturalWidth) *
            shadowImage!.width +
          'px';
        box.style.top =
          (element.plate.box.ymin / shadowImage!.naturalHeight) *
            shadowImage!.height +
          'px';
        box.style.width =
          ((element.plate.box.xmax - element.plate.box.xmin) /
            shadowImage!.naturalWidth) *
            shadowImage!.width +
          'px';
        box.style.height =
          ((element.plate.box.ymax - element.plate.box.ymin) /
            shadowImage!.naturalHeight) *
            shadowImage!.height +
          'px';
        overlayDiv.appendChild(box);
      }
    });
  }

  async submit() {
    function submitData(
      lat: number,
      long: number,
      dt: Date,
      img: string,
    ): Promise<any> {
      return new Promise((resolve, reject) => {
        let request = new XMLHttpRequest();
        request.addEventListener('readystatechange', () => {
          if (request.readyState === 4 && request.status === 200) {
            let data = JSON.parse(request.responseText);
            resolve(data);
          } else if (request.readyState === 4) {
            reject('error getting resources');
          }
        });

        compressJpegDataUrl(img, 0.3).then((newImg) => {
          const formData = new FormData();
          formData.append('latitude', JSON.stringify(lat));
          formData.append('longitude', JSON.stringify(long));
          formData.append('datetime', dt.toISOString());
          formData.append('image', newImg);

          request.open('POST', 'https://bikeaction.org/lazer/submit/');
          request.send(formData);
        });
      });
    }

    this.loadingCtrl
      .create({
        message: 'Processing...',
        duration: 20000,
      })
      .then((loader) => {
        loader.present();
        const violationTime = new Date(this.violationData.time!);
        this.photos.fetchPicture(this.violationData.image!).then((photo) => {
          submitData(
            this.violationData.position!.coords!.latitude,
            this.violationData.position!.coords!.longitude,
            violationTime,
            photo.webviewPath,
          )
            .then((data: any) => {
              this.violationData.raw = data;
              this.storage.set(
                'violation-' + this.violationId,
                this.violationData,
              );
              if (data.vehicles.length == 1) {
                this.selectVehicle(0);
              }
              this.violationData.processed = true;
              this.violationData.address = data.address;
              this.storage
                .set('violation-' + this.violationId, this.violationData)
                .then((data) => {
                  setTimeout(() => {
                    this.changeDetectorRef.detectChanges();
                    loader.dismiss();
                    this.drawHitBoxes();
                  }, 100);
                });
            })
            .catch((err: any) => {
              console.log(err);
              setTimeout(() => {
                loader.dismiss();
              }, 100);
            });
        });
      });
  }

  async openModal() {
    const chooseViolationModal = await this.modalCtrl.create({
      component: ChooseViolationModalComponent,
    });
    chooseViolationModal.present();

    const { data, role } = await chooseViolationModal.onWillDismiss();

    if (role === 'save') {
      this.violationData.violationType = data;
      this.storage
        .set('violation-' + this.violationId, this.violationData)
        .then((data) => {
          this.changeDetectorRef.detectChanges();
        });
    }

    this.openViolationModal();
  }

  async openViolationModal() {
    const confirmViolationDetailsModal = await this.modalCtrl.create({
      component: ConfirmViolationDetailsModalComponent,
      componentProps: { violation: this.violationData },
    });
    confirmViolationDetailsModal.present();
    const { data, role } = await confirmViolationDetailsModal.onWillDismiss();

    if (role === 'save') {
      console.log(data);
    }
  }

  ngOnInit() {
    this.violationId = parseInt(
      this.route.snapshot.paramMap.get('violationId') as string,
    );
    this.storage.get('violation-' + this.violationId).then((data) => {
      this.violationData = data;
    });
  }
}
