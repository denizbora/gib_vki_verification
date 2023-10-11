$(document).ready(function () {
     // Radio button seçimine göre input adını belirle
     $('input[name="sorguType"]').change(function () {
        if ($(this).val() === "TC") {
            $('#sorguInput').attr('name', 'tckn1');
            $('#sorguInput1').attr('name', 'vkn1');
            $('#sorguInput').attr('placeholder', 'TC Kimlik No Giriniz');
        } else {
            $('#sorguInput').attr('name', 'vkn1');
            $('#sorguInput1').attr('name', 'tckn1');
            $('#sorguInput').attr('placeholder', 'VKN Giriniz');
        }
    });

    var iller = $('#iller');
    var vergidaireleri = $('#vergidaireleri');

    // İlk seçim kutusunu doldur
    var jsonFileURL = 'static/vergidaireleri.json';
    $.getJSON(jsonFileURL, function (jsonData) {
    jsonData.forEach(function (il) {
        iller.append($('<option>', {
            value: Object.keys(il)[0],
            text: il[Object.keys(il)[0]]
        }));
    });

    // İlk seçim kutusu değeri değiştikçe ikinci seçim kutusunu güncelle
    iller.on('change', function () {
        var selectedIl = $(this).val();
        vergidaireleri.empty().prop('disabled', !selectedIl);
        

        if (selectedIl) {
            var ilData = jsonData.find(function (il) {
                return selectedIl === Object.keys(il)[0];
            });

            if (ilData && ilData.vergiDaireleri) {
                ilData.vergiDaireleri.forEach(function (vd) {
                    vergidaireleri.append($('<option>', {
                        value: vd.kod,
                        text: vd.vdadi
                    }));
                });
            }
        }
    });
})
});
